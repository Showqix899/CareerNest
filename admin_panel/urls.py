# urls.py
from rest_framework.routers import DefaultRouter
from .views import CityViewSet,SkillViewSet

router = DefaultRouter()
router.register("cities", CityViewSet, basename="city")
router.register("skills", SkillViewSet, basename="skill")

urlpatterns = router.urls