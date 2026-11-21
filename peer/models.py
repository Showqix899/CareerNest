# peers/models.py
import uuid
from django.conf import settings
from django.db import models
from django.db.models import F, Q

User = settings.AUTH_USER_MODEL


class PeerRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # sender index is covered by the unique constraint below
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="sent_peer_requests", db_index=False,
    )
    # receiver index is covered by the composite index below
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="received_peer_requests", db_index=False,
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(sender=F("receiver")),
                name="prevent_self_peer_request",
            ),
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_directional_peer_request",
            ),
        ]
        indexes = [
            models.Index(
                fields=["receiver", "-created_at"],
                condition=Q(status="PENDING"),
                name="peer_incoming_pending_idx",
            ),
            models.Index(
                fields=["receiver", "status"],
                name="peer_receiver_status_idx",
            ),
        ]


class Peer(models.Model):
    """Accepted connection. One row per pair, stored in canonical order (user_a < user_b)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_a = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="peers_as_a", db_index=False,
    )
    user_b = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="peers_as_b",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(user_a__lt=F("user_b")),
                name="peer_canonical_order",
            ),
            models.UniqueConstraint(
                fields=["user_a", "user_b"], name="unique_peer_pair"
            ),
        ]

    @staticmethod
    def ordered(u1, u2):
        return (u1, u2) if u1.pk < u2.pk else (u2, u1)