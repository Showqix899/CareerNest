from django.shortcuts import render
from django.db import transaction 
from django.db.models import Q,F
from django.core.cache import cache 

from .models import PeerRequest
from .forms import SendPeerRequestForm,AcceptPeerRequestForm,RejectPeerRequestForm
# Create your views here.

PEER_CACHE_TTL = 300 #seconds


#generate cache key
def peers_cache_key(user_id):
    return f"peers:{user_id}"



#geting peers field
def peer_list(request):
    
    try:
        
        key = peers_cache_key(request.user.id)
        peers=cache.get(key)
        
        if peers:
            return render(request,"peers/peers_list.html",{"peers":peers})
        else:
            
            #get peers list
            peer_list = PeerRequest.objects.filter(Q(sender=request.user) | Q(receiver=request.user) , Q(status=PeerRequest.Status.ACCEPTED)).select_related("sender__profiles","receiver__profiles").order_by("-updated_at")
            peers={}
            
            #extracting only neccessarie info
            for r in peer_list:
                peer = r.receiver if r.sender_id == request.user.id else r.sender
                if peer.id in peers:
                    continue
                
                profile= getattr(peer,"profiles",None)
                pic = profile.profile_pic if profile and profile.profile_pic else None
                
                peers[peer.id]={
                    "id":peer.id,
                    "profile_id":profile.id,
                    "full_name":peer.full_name,
                    "email":peer.email
                }
                return render(request,"peers/peers_list.html",{"peers":peers})
            
    except Exception as e:
        pass
    
        