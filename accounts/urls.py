from django.urls import path
from .views import UserRegisterView, ActivateAccountView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),
]