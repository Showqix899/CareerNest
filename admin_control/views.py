from django.shortcuts import render,redirect,get_object_or_404
from core.decorator import admin_required

from user_profile.models import City,CV,Skill,ProjectDescription,UserProfile

@admin_required # Using your new decorator!
def admin_dashboard(request):
    cities = City.objects.all()
    skills = Skill.objects.all()
    return render(request, "admin/dashboard.html", {
        "cities": cities,
        "skills": skills
    })