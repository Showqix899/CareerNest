from django.contrib import admin
from .models import PeerRequest
# Register your models here.
@admin.register(PeerRequest)

class MyModelAdmin(admin.ModelAdmin):
    pass