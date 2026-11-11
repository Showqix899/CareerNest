
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import PeerRequest
from .forms import (
    SendPeerRequestForm,
    AcceptPeerRequestForm,
    RejectPeerRequestForm,
)


PEER_CACHE_TTL = 300
PAGE_SIZE = 10


# =====================================================
# CACHE HELPERS
# =====================================================

def cache_version_key(namespace, user_id):
    return f"{namespace}:version:{user_id}"


def get_cache_version(namespace, user_id):
    key = cache_version_key(namespace, user_id)

    # Initialize version if it does not exist
    cache.add(key, 1, timeout=None)

    return cache.get(key, 1)


def invalidate_user_cache(namespace, user_id):
    """
    Increment cache version.
    Old cached data becomes inaccessible automatically.
    """

    key = cache_version_key(namespace, user_id)

    if not cache.add(key, 1, timeout=None):
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 2, timeout=None)


def invalidate_peer_list(user_id):
    invalidate_user_cache("peers", user_id)


def invalidate_peer_requests(user_id):
    invalidate_user_cache("peer_requests", user_id)


# =====================================================
# CACHE KEY GENERATORS
# =====================================================

def peers_cache_key(user_id):
    version = get_cache_version("peers", user_id)

    return f"peers:{user_id}:v{version}"


def peer_request_cache_key(user_id):
    version = get_cache_version("peer_requests", user_id)

    return f"peer_requests:{user_id}:v{version}"


# =====================================================
# PROFILE DATA HELPER
# =====================================================

def get_peer_profile_data(user):
    """
    Extract required peer information.
    """

    profile = getattr(user, "profiles", None)

    profile_pic = None

    if profile and profile.profile_pic:
        profile_pic = profile.profile_pic.url

    return {
        "id": user.id,
        "profile_id": profile.id if profile else None,
        "full_name": user.full_name,
        "email": user.email,
        "pic": profile_pic,
    }


# =====================================================
# PEER LIST
# =====================================================

@login_required
def peer_list(request):

    key = peers_cache_key(request.user.id)

    peers = cache.get(key)

    if peers is None:

        # Fetch accepted relationships
        queryset = (
            PeerRequest.objects
            .filter(
                Q(sender=request.user) | Q(receiver=request.user),
                status=PeerRequest.Status.ACCEPTED
            )
            .select_related(
                "sender__profiles",
                "receiver__profiles"
            )
            .order_by("-updated_at")
        )

        peers = []
        seen_peers = set()

        for peer_request in queryset:

            # Identify the other user
            peer = (
                peer_request.receiver
                if peer_request.sender_id == request.user.id
                else peer_request.sender
            )

            # Prevent duplicate peers
            if peer.id in seen_peers:
                continue

            seen_peers.add(peer.id)

            peers.append(get_peer_profile_data(peer))

        # Cache complete peer list
        cache.set(key, peers, PEER_CACHE_TTL)

    # Paginate cached peer data
    paginator = Paginator(peers, PAGE_SIZE)

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "peers": page_obj,
        "page_obj": page_obj,
    }

    return render(
        request,
        "peers/peers_list.html",
        context
    )


# =====================================================
# INCOMING PEER REQUESTS
# =====================================================

@login_required
def incoming_peer_requests(request):

    key = peer_request_cache_key(request.user.id)

    peer_requests = cache.get(key)

    if peer_requests is None:

        queryset = (
            PeerRequest.objects
            .filter(
                receiver=request.user,
                status=PeerRequest.Status.PENDING
            )
            .select_related(
                "sender",
                "sender__profiles"
            )
            .order_by("-created_at")
        )

        peer_requests = []

        for peer_request in queryset:

            sender = peer_request.sender

            peer_data = get_peer_profile_data(sender)

            peer_data.update({
                "request_id": str(peer_request.id),
                "created_at": peer_request.created_at,
            })

            peer_requests.append(peer_data)

        # Cache complete incoming request list
        cache.set(key, peer_requests, PEER_CACHE_TTL)

    # Paginate cached data
    paginator = Paginator(peer_requests, PAGE_SIZE)

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "peer_requests": page_obj,
        "page_obj": page_obj,
    }

    return render(
        request,
        "peers/incoming_peer_requests.html",
        context
    )


# =====================================================
# SEND PEER REQUEST
# =====================================================

@login_required
@require_POST
def send_peer_request(request):

    form = SendPeerRequestForm(request.POST)

    if not form.is_valid():

        messages.error(request, "Invalid peer request.")

        return redirect("peer_list")

    receiver = form.cleaned_data["receiver"]

    if receiver == request.user:

        messages.error(
            request,
            "You cannot send a request to yourself."
        )

        return redirect("peer_list")

    try:

        with transaction.atomic():

            # Check existing request in same direction
            existing_request = (
                PeerRequest.objects
                .select_for_update()
                .filter(
                    sender=request.user,
                    receiver=receiver
                )
                .first()
            )

            # Check reverse-direction request
            reverse_request = (
                PeerRequest.objects
                .select_for_update()
                .filter(
                    sender=receiver,
                    receiver=request.user
                )
                .first()
            )

            # Already connected
            if (
                existing_request
                and existing_request.status == PeerRequest.Status.ACCEPTED
            ) or (
                reverse_request
                and reverse_request.status == PeerRequest.Status.ACCEPTED
            ):

                outcome = "connected"

            # Request already sent
            elif (
                existing_request
                and existing_request.status == PeerRequest.Status.PENDING
            ):

                outcome = "pending"

            # Receiver already sent a request to current user
            elif (
                reverse_request
                and reverse_request.status == PeerRequest.Status.PENDING
            ):

                outcome = "incoming"

            # Reuse rejected/cancelled request
            elif existing_request:

                existing_request.status = PeerRequest.Status.PENDING

                existing_request.save(
                    update_fields=["status", "updated_at"]
                )

                outcome = "sent"

            # Create a new request
            else:

                PeerRequest.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    status=PeerRequest.Status.PENDING
                )

                outcome = "sent"

    except IntegrityError:

        messages.warning(
            request,
            "A peer request already exists."
        )

        return redirect("peer_list")

    # Invalidate receiver's incoming request cache
    if outcome == "sent":

        invalidate_peer_requests(receiver.id)

        messages.success(
            request,
            "Peer request sent successfully."
        )

    elif outcome == "connected":

        messages.info(
            request,
            "You are already connected with this user."
        )

    elif outcome == "pending":

        messages.warning(
            request,
            "You have already sent a pending request to this user."
        )

    elif outcome == "incoming":

        messages.info(
            request,
            "This user has already sent you a request. Check your incoming requests."
        )

    return redirect("peer_list")


# =====================================================
# ACCEPT PEER REQUEST
# =====================================================

@login_required
@require_POST
def accept_peer_request(request):

    form = AcceptPeerRequestForm(request.POST)

    if not form.is_valid():

        messages.error(request, "Invalid peer request.")

        return redirect("incoming_peer_requests")

    request_id = form.cleaned_data["request_id"]

    with transaction.atomic():

        peer_request = get_object_or_404(
            PeerRequest.objects.select_for_update(),
            id=request_id,
            receiver=request.user,
            status=PeerRequest.Status.PENDING
        )

        peer_request.status = PeerRequest.Status.ACCEPTED

        peer_request.save(
            update_fields=["status", "updated_at"]
        )

        sender_id = peer_request.sender_id
        receiver_id = peer_request.receiver_id

    # Invalidate affected caches
    invalidate_peer_requests(receiver_id)

    invalidate_peer_list(sender_id)
    invalidate_peer_list(receiver_id)

    messages.success(
        request,
        f"You are now connected with {peer_request.sender.full_name}."
    )

    return redirect("incoming_peer_requests")


# =====================================================
# REJECT PEER REQUEST
# =====================================================

@login_required
@require_POST
def reject_peer_request(request):

    form = RejectPeerRequestForm(request.POST)

    if not form.is_valid():

        messages.error(request, "Invalid peer request.")

        return redirect("incoming_peer_requests")

    request_id = form.cleaned_data["request_id"]

    with transaction.atomic():

        peer_request = get_object_or_404(
            PeerRequest.objects.select_for_update(),
            id=request_id,
            receiver=request.user,
            status=PeerRequest.Status.PENDING
        )

        peer_request.status = PeerRequest.Status.REJECTED

        peer_request.save(
            update_fields=["status", "updated_at"]
        )

        receiver_id = peer_request.receiver_id

    # Invalidate incoming request cache
    invalidate_peer_requests(receiver_id)

    messages.success(
        request,
        "Peer request rejected successfully."
    )

    return redirect("incoming_peer_requests")
