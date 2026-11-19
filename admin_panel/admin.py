from django.contrib import admin
from .models import Skill,City


@admin.register(Skill)
@admin.register(City)
class MyModelAdmin(admin.ModelAdmin):
    pass
