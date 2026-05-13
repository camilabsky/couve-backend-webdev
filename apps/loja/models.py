from django.db import models
from django.conf import settings


class ItemLoja(models.Model):
    horta = models.ForeignKey(
        'hortas.Horta',
        on_delete=models.CASCADE,
        related_name='itens_loja',
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='loja/', blank=True, null=True)
    preco_moedas = models.PositiveIntegerField()
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} ({self.preco_moedas} moedas)'

    @property
    def disponivel(self):
        return self.ativo and self.estoque > 0


class Compra(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compras',
    )
    item = models.ForeignKey(
        ItemLoja,
        on_delete=models.PROTECT,
        related_name='compras',
    )
    quantidade = models.PositiveIntegerField(default=1)
    total_moedas = models.PositiveIntegerField()
    realizada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario} comprou {self.item} x{self.quantidade}'
