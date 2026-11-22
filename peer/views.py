from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import Response
from django.db.models import Q


from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse
)

from .models import Peer,PeerRequest
from .serializers import SendPeerRequestSerializer,PeerRequestSerialzer

class SendPeerRequestView(APIView):
    
    permission_classes=[IsAuthenticated]
    @extend_schema(
        tags=["Send Peer Request"],
        summary=["Sending peer request to another user"],
        request=SendPeerRequestSerializer,
    )
    def post(self,request):
        
        serializer= SendPeerRequestSerializer(
            data = self.request.data,
            context={"request":request}
        )
        
        if serializer.is_valid():
            
            peer_request = serializer.save()
            
            return Response(
                {
                    "message":"peer request has been send",
                
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
class ListPeerRequestView(APIView):
    
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        
        try:
            peer_requests = PeerRequest.objects.filter(
                        receiver=request.user
                    )
            if not peer_requests:
                return Response(
                    {
                        "message":"no request found"
                    }
                )
            
            serializer = PeerRequestSerialzer(peer_requests,many=True)
            
           
            return Response(
                {
                    "peer_requests":serializer.data
                },
                status=200
            )
                
        except Exception as e:
            
            return Response(
                {
                    "message":str(e)
                    
                },
                status=400
            )