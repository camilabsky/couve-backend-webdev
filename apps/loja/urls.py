from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ItemLojaViewSet, CompraViewSet

router = DefaultRouter()
router.register('itens', ItemLojaViewSet, basename='itemloja')
router.register('compras', CompraViewSet, basename='compra')

urlpatterns = [path('', include(router.urls))]

