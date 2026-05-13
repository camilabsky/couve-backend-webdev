from django.db import models
from django.conf import settings


class Conquista(models.Model):
    TIPO_CHOICES = [
        ('missoes', 'Missões Concluídas'),
        ('nivel', 'Nível Atingido'),
        ('moedas', 'Moedas Acumuladas'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    icone = models.ImageField(upload_to='conquistas/', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor_necessario = models.PositiveIntegerField(
        help_text='Ex: 10 missões, nível 5, 500 moedas'
    )

    def __str__(self):
        return self.nome


class ConquistaUsuario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conquistas',
    )
    conquista = models.ForeignKey(
        Conquista,
        on_delete=models.CASCADE,
        related_name='usuarios',
    )
    desbloqueada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'conquista')

    def __str__(self):
        return f'{self.usuario} desbloqueou {self.conquista}'
