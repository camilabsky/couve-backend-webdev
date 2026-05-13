from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count

from .models import ItemLoja, Compra
from .serializers import ItemLojaSerializer, CompraSerializer


class ItemLojaViewSet(viewsets.ModelViewSet):
    """CRUD de itens da loja (produtos com controle de estoque)."""

    queryset = ItemLoja.objects.select_related('horta').all()
    serializer_class = ItemLojaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        apenas_disponiveis = self.request.query_params.get('disponivel')
        if apenas_disponiveis == 'true':
            qs = qs.filter(ativo=True, estoque__gt=0)
        return qs


class CompraViewSet(viewsets.ModelViewSet):
    """Registro de vendas. Criação desconta estoque e moedas do usuário."""

    serializer_class = CompraSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # vendas não são editáveis

    def get_queryset(self):
        if self.request.user.is_staff:
            return Compra.objects.select_related('usuario', 'item').all()
        return Compra.objects.select_related('item').filter(usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='relatorio',
            permission_classes=[permissions.IsAdminUser])
    def relatorio(self, request):
        """Relatório de vendas: total de transações, moedas movimentadas e ranking por item."""
        compras = Compra.objects.select_related('item').all()

        total_vendas = compras.count()
        total_moedas = compras.aggregate(total=Sum('total_moedas'))['total'] or 0

        por_item = (
            compras
            .values('item__nome')
            .annotate(qtd_vendida=Sum('quantidade'), receita_moedas=Sum('total_moedas'))
            .order_by('-receita_moedas')
        )

        return Response({
            'total_vendas': total_vendas,
            'total_moedas_movimentadas': total_moedas,
            'vendas_por_item': list(por_item),
        })
