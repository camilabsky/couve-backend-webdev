from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HortaViewSet

router = DefaultRouter()
router.register('', HortaViewSet, basename='horta')

urlpatterns = [path('', include(router.urls))]

