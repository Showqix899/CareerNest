import uuid
from django.db import models
from django.db.models import Q,F
from accounts.models import User
# Create your models here.

class PeerRequest(models.Model):
    
    #status of request peers
    class Status(models.TextChoices):
        
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED","Rejected"
        CANCELLED = "CANCELLED","Cancelled"
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="send_peer_request"
    )
    
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recieved_peer_request"
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        
        #check constraints
        constraints = [
            models.CheckConstraint(
                condition=~Q(sender=F("receiver")),
                name="prevent_self_peer_request"
            ),
            
            models.UniqueConstraint(
                fields=["sender","receiver"],
                name="unique_directional_peer_request"
            ),
        ]
        
        indexes = [
            models.Index(
                fields=["receiver","status","-created_at"],
                name="peer_incomming_idx"
            ),
            
            models.Index(
                fields=["sender","status","-created_at"],
                name="peer_outgoing_idx"
            )
        ]