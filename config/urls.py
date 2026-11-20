"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .health_check import health
from django.urls import include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("health",health,name="health"),
    path("api/user/",include("accounts.urls")),
    path("api/admin/",include("admin_panel.urls")),
    
    
     # 1) The raw schema file (JSON/YAML). Swagger and Redoc read from this.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # 2) Swagger UI page, open: /api/docs/
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # 3) Redoc page (optional, another style), open: /api/redoc/
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
