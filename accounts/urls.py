from django.urls import path
from .views import UserRegisterView, ActivateAccountView,LoginView,LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),
    path("login/",LoginView.as_view(),name="login"),
    path("token/refresh/",TokenRefreshView.as_view(),name="token_refresh"),
    path("logout/",LogoutView.as_view(),name="logout"),
]