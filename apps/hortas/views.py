from rest_framework import viewsets, permissions

from .models import Horta
from .serializers import HortaSerializer


class HortaViewSet(viewsets.ModelViewSet):
    """CRUD de hortas comunitárias."""

    queryset = Horta.objects.select_related('gestor').all()
    serializer_class = HortaSerializer
    permission_classes = [permissions.IsAuthenticated]
