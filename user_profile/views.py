from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import transaction
from django.views.decorators.http import require_POST

from core.decorator import admin_required
from .models import CV,Skill,ProjectDescription,UserProfile,City,ProjectMedia
from .forms import UserCVForms,UserProfileForm,ProjectDescriptionForm,SkillForm,CityForm,ProjectMediaForm
from peers.models import PeerRequest
from accounts.models import User
from django.db.models import Q





# Create your views here.
#user profile 
@login_required
def user_profile(request):
    context = {
        "profile": (
            UserProfile.objects.filter(user=request.user)
            .select_related("city")
            .prefetch_related("skills")
            .order_by("pk")   # lets the template's .first reuse the cached result
        ),
        "projects": ProjectDescription.objects.filter(user=request.user).only("id", "title", "description"),
        "cvs": CV.objects.filter(user=request.user).only("id", "title"),
    }
    return render(request, "user_profile/user_profile.html", {"context": context})



#create city
def create_city(request):
    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_city") # Redirect on success (PRG Pattern)
    else:
        form = CityForm()

    # Fetch all existing cities to display in the list below the form
    cities = City.objects.all()

    context = {
        "form": form,
        "cities": cities
    }
    return render(request, "user_profile/city.html", context)
    
    
#city instance delete #admin
def delete_city(request, uuid):
    if request.method == "POST":
        try:
            city = City.objects.get(id=uuid)
            city.delete()
        except City.DoesNotExist:
            pass
            
    return redirect("create_city")



# Create your views here. #admin 
def create_skill(request):
    try:
        if request.method == "POST":
            form = SkillForm(request.POST)
            if form.is_valid():
                form.save() 
                return redirect("create_skill")
        else:
            form = SkillForm()

        # Always fetch skills so they render correctly on both GET and POST
        skills = Skill.objects.all()
        
        context = {
            "form": form,
            "skills": skills
        }
        return render(request, "user_profile/skill.html", context)

    except ValidationError as e:
        error_message = str(e)
        skills = Skill.objects.all()
        return render(request, "user_profile/skill.html", {"form": form, "skills": skills, "error_message": error_message})


# skill instance delete #admin 
def delete_skill(request, uuid):
    if request.method == "POST":
        try:
            skill = Skill.objects.get(id=uuid)
            skill.delete()
        except Skill.DoesNotExist:
            pass
            
    return redirect("create_skill")



#user profile view 
@login_required
def user_profile_create(request):
    # Get the existing profile or initialize an UNSAVED instance in memory
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile:
        profile = UserProfile(user=request.user) # Does NOT write to DB yet!

    try:
        if request.method == "POST":
            # Include request.FILES in case your profile has avatar/image uploads
            profile_form = UserProfileForm(
                request.POST,
                request.FILES,
                instance=profile
            )
        
            if profile_form.is_valid():
                with transaction.atomic():
                    # form.save() automatically handles saving the instance and m2m fields
                    profile_form.save()
                
                return redirect("user_profile")
        else:
            # Pre-fill the form with the existing profile data on GET requests
            profile_form = UserProfileForm(instance=profile)

        return render(request, "user_profile/user_profile_create.html", {"form": profile_form})  

    except Exception as e:
        return render(request, "user_profile/error.html", {"message": f"error saving profile details : {str(e)}"})


#user profile update
@login_required
def user_profile_update(request):
    
    #get user profile 
    profile = UserProfile.objects.filter(user=request.user).first()
    
    if not profile:
        return render(request,"user_profile/error.html",{"message":"user not found"})
    
    if request.method == "POST":
        
        form = UserProfileForm(request.POST,instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
        
    else:
        
        form = UserProfileForm(instance=profile)
        return render(request,"user_profile/user_profile_create.html",{"form":form})


#add projects 
@login_required
def add_projects(request):
    if request.method == "POST":
        form = ProjectMediaForm(request.POST, request.FILES, project=project)
        
        if form.is_valid():
            try:
                # 1. Create the instance in memory without saving to DB yet
                project = form.save(commit=False)
                
                # 2. Attach the relation: 
                # UNCOMMENT ONE OF THE TWO BELOW DEPENDING ON YOUR MODEL DEFINITION:
                
                # Option A: If ProjectDescription links directly to User
                project.user = request.user 
                
                # Option B: If ProjectDescription links to UserProfile instead
                # profile = UserProfile.objects.get(user=request.user)
                # project.user_profile = profile # (Change 'user_profile' to match your model field name)
                
                # 3. Now save it to the database
                project.save()
                return redirect("user_profile")
                
            except Exception as e:
                # This will show you the EXACT database/attribute error on the screen
                return render(request, "user_profile/error.html", {"message": f"Error saving project: {str(e)}"})
        else:
            # If form is invalid, print/inspect errors or re-render form
            print(form.errors) # Check your terminal for form errors!
    else:
        form = ProjectDescriptionForm()
        
    return render(request, "user_profile/add_project.html", {"form": form})


#update projects
@login_required
def update_projects(request, uuid):
    # Fetch a single instance belonging to the logged-in user (or return 404)
    project = ProjectDescription.objects.get(id=uuid)

    if request.method == "POST":
        # Pass request.POST and the single instance
        form = ProjectDescriptionForm(request.POST, instance=project)
        
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        # Pre-fill the form with the existing project data on GET requests
        form = ProjectDescriptionForm(instance=project)

    # This handles both GET requests and invalid POST submissions (showing form errors)
    return render(request, "user_profile/add_project.html", {"form": form})

#project delete 
@login_required
def delete_project(request,uuid):
    
    project = ProjectDescription.objects.filter(id=uuid)
        
    if not project:
        return render(request,"user_profile/error.html",{"message":f"project not found"})
    
    project.delete()
    return redirect("user_profile")

# User CV Upload
@login_required
def user_cv_add(request):
    if request.method == "POST":
        # Pass both request.POST and request.FILES for file uploads
        form = UserCVForms(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. Create instance in memory without saving to DB yet
            cv = form.save(commit=False)
            
            # 2. Attach the logged-in user (adjust to cv.user_profile if linked to profile instead)
            cv.user = request.user 
            
            # 3. Save to database
            cv.save()
            return redirect("user_profile")
    else:
        form = UserCVForms()
        
    return render(request, "user_profile/add_cv.html", {"form": form})


# User CV Delete
@login_required
def user_cv_delete(request, uuid):
    cv = get_object_or_404(CV, id=uuid)
    
    # Ensure deletion only happens on POST requests for security
    if request.method == "POST":
        cv.delete()
        
    return redirect("user_profile")

#project details 
@login_required
def project_detail(request, pk):
    # Use prefetch_related('media') to fetch the project and all its 
    # related images/videos efficiently in minimal database queries.
    project = get_object_or_404(
        ProjectDescription.objects.prefetch_related('media'),
        id=pk,
        user=request.user  # Ensures the user can only view their own projects
    )

    context = {
        'project': project,
    }
    return render(request, 'user_profile/project_detail.html', context)
    

        
@login_required
def add_project_media(request, project_id):
    # Ensure the user only edits their own projects
    project = get_object_or_404(ProjectDescription, id=project_id, user=request.user)

    if request.method == 'POST':
        form = ProjectMediaForm(request.POST, request.FILES, project=project)
        if form.is_valid():
            form.save()
            # Redirect back to project detail or edit page
            return redirect('project_detail', pk=project.id)
    else:
        form = ProjectMediaForm(project=project)

    context = {
        'project': project,
        'form': form,
    }
    return render(request, 'user_profile/add_media.html', context)


@login_required
@require_POST
def remove_project_media(request, media_id):
    # Fetch the media item and make sure it belongs to a project owned by the logged-in user
    media_item = get_object_or_404(
        ProjectMedia, 
        id=media_id, 
        project__user=request.user
    )
    
    project_id = media_item.project.id
    
    # Optional: Delete the actual file from storage (MEDIA_ROOT)
    if media_item.file:
        media_item.file.delete(save=False)
        
    # Delete the database record
    media_item.delete()
    
    return redirect('project_detail', pk=project_id)


@login_required
def get_user_profile_details(request, user_id):
    if user_id == request.user.id:
        return redirect("user_profile")

    target = get_object_or_404(
        User.objects.only("id", "full_name", "email"),
        pk=user_id, is_active=True,
    )

    # One query covers both directions (max 2 rows due to the unique constraint)
    links = PeerRequest.objects.filter(
        Q(sender=request.user, receiver=target) | Q(sender=target, receiver=request.user)
    ).values("id", "sender_id", "status")

    peer_status, peer_request_id = "none", None   # none | sent | incoming | connected
    for link in links:
        if link["status"] == PeerRequest.Status.ACCEPTED:
            peer_status, peer_request_id = "connected", None
            break
        if link["status"] == PeerRequest.Status.PENDING:
            if link["sender_id"] == request.user.id:
                peer_status = "sent"
            else:
                peer_status, peer_request_id = "incoming", str(link["id"])

    # order_by("pk") matters: the template calls .first, which only reuses the
    # prefetched/cached result when the queryset is already ordered.
    profile_qs = (
        UserProfile.objects.filter(user=target)
        .select_related("city")
        .prefetch_related("skills")
        .order_by("pk")
    )

    context = {
        "profile": profile_qs,
        "projects": ProjectDescription.objects.filter(user=target).only("id", "title", "description"),
        "cvs": CV.objects.filter(user=target).only("id", "title"),
        "owner": target,
        "is_other": True,
        "peer_status": peer_status,
        "peer_request_id": peer_request_id,
    }
    return render(request, "user_profile/user_profile.html", {"context": context})
            
    

