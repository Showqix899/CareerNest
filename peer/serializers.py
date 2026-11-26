from rest_framework import serializers
from .models import Peer,PeerRequest
from .models import User
from django.db.models import Q



from django.db.models import Q
from rest_framework import serializers

from .models import Peer, PeerRequest, User


class SendPeerRequestSerializer(serializers.Serializer):
    """input receiver id"""

    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def _existing_request(self, other_user):
        me = self.context["request"].user
        return PeerRequest.objects.filter(
            Q(sender=me, receiver=other_user) | Q(sender=other_user, receiver=me)
        ).first()

    def validate_receiver(self, value):
        me = self.context["request"].user

        if value.pk == me.pk:
            raise serializers.ValidationError("You can not send a request to yourself")

        existing = self._existing_request(value)

        if existing:
            if existing.status == PeerRequest.STATUS.pending:
                raise serializers.ValidationError("A peer request already exists")
            if existing.status == PeerRequest.STATUS.accepted:
                raise serializers.ValidationError("You are already peers")
            # rejected -> allowed, handled in create()

        return value

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver = validated_data["receiver"]

        existing = self._existing_request(receiver)

        # reopen a previously rejected request instead of creating a duplicate
        if existing and existing.status == PeerRequest.STATUS.reject:
            existing.sender = sender
            existing.receiver = receiver
            existing.status = PeerRequest.STATUS.pending
            existing.save()
            return existing

        return PeerRequest.objects.create(sender=sender, receiver=receiver)
    
#peer request serializer
class PeerRequestSerialzer(serializers.ModelSerializer):
    
    class Meta:
        model = PeerRequest
        fields= ["id","sender","receiver","status","created_at"]
        read_only_fields = fields
    
        
        
        
        