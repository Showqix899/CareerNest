from django.urls import path
from . import views

urlpatterns = [
    # Main User Profile View
    path("profile/", views.user_profile, name="user_profile"),
    
    # City Management (Admin)
    path("city/create/", views.create_city, name="create_city"),
    path("city/delete/<uuid:uuid>/", views.delete_city, name="delete_city"),
    
    # Skill Management (Admin)
    path("skill/create/", views.create_skill, name="create_skill"),
    path("skill/delete/<uuid:uuid>/", views.delete_skill, name="delete_skill"),
    
    # User Profile Create & Update
    path("profile/create/", views.user_profile_create, name="user_profile_create"),
    path("profile/update/", views.user_profile_update, name="user_profile_update"),
    
    # Project Management
    path("projects/add/", views.add_projects, name="add_projects"),
    path("projects/update/<uuid:uuid>/", views.update_projects, name="update_projects"),
    path("projects/delete/<uuid:uuid>/", views.delete_project, name="delete_project"),
    
    # CV Management
    path("cv/add/", views.user_cv_add, name="user_cv_add"),
    path("cv/delete/<uuid:uuid>/", views.user_cv_delete, name="user_cv_delete"),
    
    # Project Detail view
    path('project/<uuid:pk>/', views.project_detail, name='project_detail'),
    
    # Media management views
    path('project/<uuid:project_id>/media/add/', views.add_project_media, name='add_project_media'),
    path('media/<uuid:media_id>/delete/', views.remove_project_media, name='remove_project_media'),
]