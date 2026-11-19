from django.contrib import admin
from .models import CV,ProjectDescription,ProjectMedia,UserProfile

@admin.register(UserProfile)
@admin.register(ProjectDescription)
@admin.register(ProjectMedia)
@admin.register(CV)


class MyModelAdmin(admin.ModelAdmin):
    pass