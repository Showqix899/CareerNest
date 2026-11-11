from django.contrib import admin
from .models import City,Skill,CV,UserProfile,ProjectDescription
# Register your models here.

@admin.register(City)
@admin.register(CV)
@admin.register(Skill)
@admin.register(ProjectDescription)
@admin.register(UserProfile)
class MyModelAdmin(admin.ModelAdmin):
    pass