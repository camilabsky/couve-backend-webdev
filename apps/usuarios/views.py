from rest_framework import viewsets, permissions

from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCadastroSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuários (clientes/voluntários/gestores)."""

    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCadastroSerializer
        return UsuarioSerializer

    def get_permissions(self):
        # cadastro é público; demais ações exigem autenticação
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
