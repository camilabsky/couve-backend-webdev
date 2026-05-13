from django.db import models
from django.conf import settings


class Horta(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    endereco = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    foto = models.ImageField(upload_to='hortas/', blank=True, null=True)
    gestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='hortas',
        limit_choices_to={'tipo': 'gestor'},
    )
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
