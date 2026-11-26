from accounts.models import User
from django.db import models
import uuid



#peer request 
class PeerRequest(models.Model):
    
    class STATUS(models.TextChoices):
        
        pending = "pending", "Pending"
        accepted = "accepted", "Accepted"
        reject = "reject", "Reject"
        
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_peer_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_peer_requests")
    status = models.CharField(
        max_length=20,
        choices=STATUS.choices,
        default=STATUS.pending,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #seting up constraints and indexes
    class Meta:
        
        constraints = [
            models.UniqueConstraint(
                fields = ["sender","receiver"],
                name="unique_sender_receiver"
            )
        ]

        indexes = [
            models.Index(fields=["receiver","status"]),
            models.Index(fields=["sender","status"])
        ]
    
    def __str__(self):
        return f"{self.sender.full_name} sent peer request to {self.receiver.full_name}"
    
    
    
#peers 
class Peer(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_receiver")
    responded_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.sender.full_name} is connected to {self.receiver.full_name}"