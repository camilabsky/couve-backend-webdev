from django.db import models
from django.conf import settings


class Missao(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('encerrada', 'Encerrada'),
    ]

    horta = models.ForeignKey(
        'hortas.Horta',
        on_delete=models.CASCADE,
        related_name='missoes',
    )
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    nivel_minimo = models.PositiveIntegerField(default=1)
    recompensa_moedas = models.PositiveIntegerField(default=0)
    recompensa_xp = models.PositiveIntegerField(default=0)
    prazo = models.DateTimeField(null=True, blank=True)
    vagas = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} ({self.horta})'

    @property
    def vagas_disponiveis(self):
        aceitas = self.participacoes.filter(status='aceita').count()
        return max(0, self.vagas - aceitas)


class ParticipacaoMissao(models.Model):
    STATUS_CHOICES = [
        ('aceita', 'Aceita'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participacoes',
    )
    missao = models.ForeignKey(
        Missao,
        on_delete=models.CASCADE,
        related_name='participacoes',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aceita')
    foto_comprovante = models.ImageField(upload_to='comprovantes/', blank=True, null=True)
    aceita_em = models.DateTimeField(auto_now_add=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'missao')

    def __str__(self):
        return f'{self.usuario} → {self.missao} [{self.status}]'
