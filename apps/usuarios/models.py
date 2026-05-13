from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('voluntario', 'Voluntário'),
        ('gestor', 'Gestor de Horta'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='voluntario')
    bio = models.TextField(blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    moedas = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    nivel = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.username} ({self.tipo})'

    @property
    def is_gestor(self):
        return self.tipo == 'gestor'

    def adicionar_xp(self, quantidade: int):
        """Adiciona XP e verifica se o usuário sobe de nível."""
        self.xp += quantidade
        xp_necessario = self.nivel * 100  # cada nível exige 100*nível XP
        if self.xp >= xp_necessario:
            self.xp -= xp_necessario
            self.nivel += 1
            self.save()
            return True  # subiu de nível
        self.save()
        return False

    def adicionar_moedas(self, quantidade: int):
        self.moedas += quantidade
        self.save()

    def gastar_moedas(self, quantidade: int):
        if self.moedas < quantidade:
            raise ValueError('Saldo insuficiente.')
        self.moedas -= quantidade
        self.save()
