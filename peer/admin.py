from django.contrib import admin

# Register your models here.
from .models import PeerRequest,Peer

@admin.register(PeerRequest)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ["sender","receiver","status","created_at"]