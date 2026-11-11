from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode,url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
import hashlib
import json
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

from .forms import RegisterForm,LoginForm
from .models import User
from user_profile.models import UserProfile
from .tasks import send_activation_email
from .tokens import account_activation_token
from django.views.decorators.http import require_GET
from django.db.models import Q




SEARCH_CACHE_TTL = 30
SEARCH_PAGE_SIZE = 10


# user registration
def register(request):
    form = RegisterForm(request.POST or None) #fill the form with user data 
    
    #check the request method and is form valid or not
    if request.method == "POST" and form.is_valid():
        user = form.save() #user user in database

        #activation token genrartion using user id
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        path = reverse("accounts:activate", kwargs={"uidb64": uid, "token": token})
        activation_link = request.build_absolute_uri(path)

        #send activation main via celery (background worker)
        send_activation_email.delay(user.email, user.full_name, activation_link)

        #redirect to success message
        return redirect("accounts:register_done")

    return render(request, "accounts/register.html", {"form": form})


def register_done(request):
    return render(request, "accounts/register_done.html")


#user activation email
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64)) #decode the uuid from params
        user = User.objects.get(pk=uid) #get user

        #create a profile for the user 
        profile = UserProfile.objects.create()
        profile.user=user
    except (TypeError, ValueError, OverflowError, ValidationError, User.DoesNotExist):
        user = None

    #basic validation for token (expired time , token integrity)
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"]) #update user to is active
        return render(request, "accounts/activation_success.html")

    return render(request, "accounts/activation_invalid.html", status=400)


#user login view 
def login_view(request):
    
    #check if the user is still authenticated
    if request.user.is_authenticated:
        
        return redirect("home") #if already authenticated return to landing page (home)
    
    form=LoginForm(request,data=request.POST or None) #fill the form with user data
    
    #check the request method and is form valid or not
    if request.method == "POST" and form.is_valid():
        
        login(request,form.get_user()) #log in the user
        
        return redirect("home")
    
    return render(
        request,
        "accounts/login.html",
        {"form":form},
    )
    
#user log out 
def logout_view(request):
    
    logout(request)
    return redirect("home")
    
    

def home(request):
    
    return render (request,"home.html")




@login_required
@require_GET
def user_search(request):
    q = request.GET.get('q', '').strip()[:100]
    users = []
    if len(q) >= 2:
        users = (
            User.objects.filter(is_active=True)
            .filter(Q(full_name__icontains=q) | Q(email__icontains=q))
            .select_related('profiles')   # avoids N+1 for profile pics
            .order_by('full_name')[:10]
        )
    return render(request, 'accounts/user_search_results.html', {'users': users, 'q': q})