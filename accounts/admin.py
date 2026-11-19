from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
@admin.register(User)

class UseAdmin(BaseUserAdmin):
    ordering=("-date_joined",)
    list_display=('email','full_name','phone','is_active','is_staff','date_joined')
    list_filter=('is_active','is_staff','is_superuser')
    search_fields = ("email", "full_name")
    readonly_fields = ("last_login", "date_joined")