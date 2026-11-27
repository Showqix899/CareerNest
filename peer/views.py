from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache  # Django's cache API: get / set / incr
from rest_framework.pagination import PageNumberPagination
from django.conf import settings

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .models import Peer, PeerRequest
from .serializers import PeerRequestSerialzer, SendPeerRequestSerializer, PeerSerializer
from config.cache_set import bump_version,_version_key,_get_version

ID_PARAM = OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)

CACHE_TTL=settings.CACHE_TTL

class PeerRequestPagination(PageNumberPagination):
    
    """pagination configuration"""
    page_size = 10 #default 10 ites per query 
    page_size_query_param = "page_size" #custom page number
    max_page_size = 50

class PeerPagination(PageNumberPagination):
    
    """pagination configuration"""
    page_size = 10 #default 10 ites per query 
    page_size_query_param = "page_size" #custom page number
    max_page_size = 50



class SendPeerRequestView(APIView):
    """Sending peer request"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Peer"],
        summary="Sending peer request to another user",
        request=SendPeerRequestSerializer,
        responses={
            200: OpenApiResponse(description="Peer request has been sent"),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "valid uuid of the user",
                value={"receiver": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = SendPeerRequestSerializer(
            data=request.data, context={"request": request}
        )
        
        """check if the serializer is valid or not and invalidate cache"""

        if serializer.is_valid():
            
            peer_request=serializer.save()
            bump_version(peer_request.receiver.id,"peer_request")
            return Response(
                {"message": "peer request has been sent"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RjectPeerRequest(APIView):
    """Rejecting peer request"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Peer"],
        summary="Rejecting peer request of another user",
        parameters=[ID_PARAM],
        request=None,
        responses={
            200: OpenApiResponse(description="Rejected peer request"),
            404: OpenApiResponse(description="Peer request not found"),
        },
    )
    def post(self, request, id):
        peer_request = get_object_or_404(PeerRequest, id=id, receiver=request.user)

        peer_request.status = PeerRequest.STATUS.reject
        peer_request.save()
        bump_version(peer_request.receiver.id,"peer_request") #invalidate cache
        return Response({"message": "rejected peer request"}, status=status.HTTP_200_OK)


class AcceptingPeerRequest(APIView):
    """Accepting peer request"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Peer"],
        summary="Accept peer request of another user",
        parameters=[ID_PARAM],
        request=None,
        responses={
            200: OpenApiResponse(description="You are now peered"),
            404: OpenApiResponse(description="There is no request to accept"),
        },
    )
    def post(self, request, id):
        
        try:
            peer_request = PeerRequest.objects.get(id=id, receiver=request.user)
            
            Peer.objects.create(sender=peer_request.sender, receiver=peer_request.receiver)
    
            peer_request.status = PeerRequest.STATUS.accepted
            peer_request.save()
            bump_version(peer_request.receiver_id,"peer_request")
            bump_version(peer_request.receiver.id,"peer")
            return Response({"message": "you are now peered"}, status=status.HTTP_200_OK)
        except PeerRequest.DoesNotExist:
            return Response({"message":"There is no request to accept"})


class ListPeerRequestView(APIView):
    """List of peer requests"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Peer"],  # groups the endpoint in Swagger
        summary="All peer requests sent to you",  # one-line description in Swagger
        parameters=[  # documents the query params so Swagger shows input boxes
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Items per page (max 50)"),
        ],
        responses={200: PeerRequestSerialzer(many=True)},  # shape of each item in "results"
    )
    def get(self, request):
        user_id = request.user.id  #get the user id 
        version = _get_version(user_id,"peer_request") #current version 
        page = request.query_params.get("page",1) #get the page number
        page_size = request.query_params.get("page_size","default") #get page size of assign default
        
        
        ## Unique per user + version + tag + page + size so each combinaton cachse 
        cache_key = f"peer_request:{user_id}:v{version}:p{page}:s{page_size}"
        
        ## get the cached data 
        cached = cache.get(cache_key)
        
        if cached is not None:
            return Response(cached,status=status.HTTP_200_OK)
        
        #cahce miss 
        # peer_requests = PeerRequest.objects.filter(receiver=request.user,status=PeerRequest.STATUS.pending).order_by("-created_at")
        peer_requests = PeerRequest.objects.filter(status=PeerRequest.STATUS.pending).select_related("sender").order_by("-created_at")
        
        #create paginator
        paginator = PeerRequestPagination()
        
        #pagnate all the peer request (10,10,10,.......)
        page_items = paginator.paginate_queryset(peer_requests,request,view=self)
        
        serializer = PeerRequestSerialzer(page_items,many=True)#serialize the data
        data = paginator.get_paginated_response(serializer.data).data #wraps in {"count "next" "pervious" "results"}
        
        cache.set(cache_key,data,CACHE_TTL) #set cache with key
        return Response(data,status=status.HTTP_200_OK)
        
        
        
class PeerListView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=["Peer"],  # groups the endpoint in Swagger
        summary="All of the peers",  # one-line description in Swagger
        parameters=[  # documents the query params so Swagger shows input boxes
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Items per page (max 50)"),
        ],
        responses={200: PeerRequestSerialzer(many=True)},  # shape of each item in "results"
    )
    def get(self,request):
        
        user_id = request.user.id #get user id 
        version = _get_version(user_id,"peer") #current version 
        page = request.query_params.get("page",1) #get the page number 
        page_size = request.query_params.get("page_size","default") #get the page size if provided 
        
        
        #unique cache key 
        cache_key = f"peer:{user_id}:v{version}:p{page}:{page_size}"
        
        ## get the cached data 
        cached = cache.get(cache_key)
        
        if cached is not None:
            #if not cached
            return Response(cached,status=status.HTTP_200_OK)
        
        peer = Peer.objects.filter().select_related("sender","receiver").order_by("-responded_at")
        
        #create pagination 
        paginator = PeerPagination()
        
        #paginate all the peers 
        page_items = paginator.paginate_queryset(peer,request,view=self)
        
        #serialized data 
        serializer = PeerSerializer(page_items,many=True)
        
        data = paginator.get_paginated_response(serializer.data).data
        cache.set(cache_key,data,CACHE_TTL)
        return Response(data,status=status.HTTP_200_OK)
        
        
        