from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("register/done/", views.register_done, name="register_done"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("login/", views.login_view, name="user_login"),
    path("logout/",views.logout_view,name="user_logout"),
    path('search/', views.user_search, name='user_search'),
    
]