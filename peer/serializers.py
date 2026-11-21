# peers/serializers.py
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from . import services
from .models import Peer, PeerRequest

User = get_user_model()


class PeerUserSerializer(serializers.ModelSerializer):
    """Minimal public info about a user. Add fields (e.g. profile picture) as needed."""

    class Meta:
        model = User
        fields = ["id", "full_name"]
        read_only_fields = fields


class PeerRequestSerializer(serializers.ModelSerializer):
    """Read-only representation of a request."""

    sender = PeerUserSerializer(read_only=True)
    receiver = PeerUserSerializer(read_only=True)

    class Meta:
        model = PeerRequest
        fields = ["id", "sender", "receiver", "status", "created_at", "responded_at"]
        read_only_fields = fields


class SendPeerRequestSerializer(serializers.Serializer):
    """Input: receiver id. Delegates all rules to services.send_request."""

    receiver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )

    def validate_receiver(self, value):
        if value.pk == self.context["request"].user.pk:
            raise serializers.ValidationError("You cannot send a request to yourself.")
        return value

    def create(self, validated_data):
        return services.send_request(
            self.context["request"].user, validated_data["receiver"]
        )

    def to_representation(self, instance):
        return PeerRequestSerializer(instance, context=self.context).data


class PeerSerializer(serializers.ModelSerializer):
    """Shows the *other* user in the pair, relative to the requesting user."""

    peer = serializers.SerializerMethodField()

    class Meta:
        model = Peer
        fields = ["id", "peer", "created_at"]
        read_only_fields = fields

    @extend_schema_field(PeerUserSerializer)
    def get_peer(self, obj):
        me = self.context["request"].user
        other = obj.user_b if obj.user_a_id == me.pk else obj.user_a
        return PeerUserSerializer(other, context=self.context).data