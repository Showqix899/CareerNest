
from django.urls import path
from .views import SendPeerRequestView,ListPeerRequestView,AcceptingPeerRequest,RjectPeerRequest,PeerListView

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
    ),
    path(
        "accepte/<uuid:id>/",
        AcceptingPeerRequest.as_view(),
        name="accepte"
    ),
    path(
        "reject/<uuid:id>/",
        RjectPeerRequest.as_view(),
        name="reject"
    ),
    path("peer-list/",PeerListView.as_view(),name="peer-list")
    
]
