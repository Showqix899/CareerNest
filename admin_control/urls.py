from django.urls import path
from . import views
urlpatterns = [
    path("dahsboard",views.admin_dashboard,name="dashboard")
]
