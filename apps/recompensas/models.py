from django.db import models
from django.conf import settings


class TransacaoMoeda(models.Model):
    TIPO_CHOICES = [
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transacoes',
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    descricao = models.CharField(max_length=255)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario} {self.tipo} {self.quantidade} moedas'
