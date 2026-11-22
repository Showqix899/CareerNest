
from django.urls import path
from .views import SendPeerRequestView,ListPeerRequestView

urlpatterns = [
    path(
        "send-request/",
        SendPeerRequestView.as_view(),
        name="send_peer_request"
    ),
    path(
        "peer-request-list",
        ListPeerRequestView.as_view(),
        name="peer-request-list"
    )
]
