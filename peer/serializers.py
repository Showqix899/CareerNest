from rest_framework import serializers
from .models import Peer,PeerRequest
from .models import User
from django.db.models import Q



#peer request serializer
class SendPeerRequestSerializer(serializers.Serializer):
    
    """input receiver id """
    
    receiver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    
    def validate_receiver(self,value):
        
        """check if the user sending itself the request"""
        if value.pk == self.context["request"].user.pk:
            
            raise serializers.ValidationError(
                "You can not send a request to yourself"
            )
            
            
        """prevent duplicate request in either direction"""
        existing_request =PeerRequest.objects.filter(
            Q(sender=self.context["request"].user.pk,receiver=value) |
            Q(sender=value,receiver=self.context["request"].user.pk)
        ).exists()
        
        if existing_request:
            raise serializers.ValidationError(
                "A peer request already exist from the reciever"
            )
            
            
        return value
            
    def create(self,validated_data):
        
        sender = self.context["request"].user
        receiver = validated_data["receiver"]
        
        """creating peer request"""
        peerRequest = PeerRequest.objects.create(
            sender=sender,
            receiver=receiver
        )
        
        return peerRequest
    
    
#peer request serializer
class PeerRequestSerialzer(serializers.ModelSerializer):
    
    class Meta:
        model = PeerRequest
        fields= ["id","sender","receiver","status","created_at"]
        read_only_fields = fields
    
        
        
        
        