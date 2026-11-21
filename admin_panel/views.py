# views.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated,IsAdminUser

from .models import City,Skill
from .serializers import CitySerializer,SkillSerializer
from .is_super_user import IsSuperUser



@extend_schema_view(
    list=extend_schema(
        summary="List cities",
        description="Returns all cities. Supports search by name.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Filter cities by name (partial match)",
                required=False,
                type=str,
            ),
        ],
    ),
    retrieve=extend_schema(summary="Get a city"),
    create=extend_schema(summary="Create a city"),
    update=extend_schema(summary="Update a city"),
    partial_update=extend_schema(summary="Partially update a city"),
    destroy=extend_schema(summary="Delete a city"),
)
@extend_schema(tags=["Cities"])
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by("name")
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    permission_classes=[IsSuperUser]
    
    
    
@extend_schema_view(
    list=extend_schema(summary="List skills", description="Returns all skills. Supports search by name."),
    retrieve=extend_schema(summary="Get a skill"),
    create=extend_schema(summary="Create a skill"),
    update=extend_schema(summary="Update a skill"),
    partial_update=extend_schema(summary="Partially update a skill"),
    destroy=extend_schema(summary="Delete a skill"),
)
@extend_schema(tags=["Skills"])
class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    permission_classes=[IsSuperUser]