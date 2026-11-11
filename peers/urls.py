from django.urls import path
from . import views


urlpatterns = [
    path(
        "list/",
        views.peer_list,
        name="peer_list"
    ),
    path(
        "peer/requests/",
        views.incoming_peer_requests,
        name="incoming_peer_requests"
    ),
    path(
        "send/",
        views.send_peer_request,
        name="send_peer_request"
    ),

    path(
        "accept/",
        views.accept_peer_request,
        name="accept_peer_request"
    ),

    path(
        "reject/",
        views.reject_peer_request,
        name="reject_peer_request"
    ),
]