from django.db import models

class Perfil(models.Model):
    nome = models.CharField(max_length=64)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'Perfil'

class Recompensas(models.Model):
    nome = models.CharField(max_length=128)
    descricao = models.TextField()
    preco = models.IntegerField()
    tipo = models.CharField(max_length=32)
    src = models.CharField(max_length=256)

    class Meta:
        db_table = 'Recompensas'

class Tarefas(models.Model):
    titulo = models.CharField(max_length=128)
    tipo = models.CharField(max_length=32)
    dificuldade = models.IntegerField()
    horta = models.CharField(max_length=128)
    descricao = models.CharField(max_length=128)
    id_perfil = models.ForeignKey(
        Perfil,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_perfil'
    )
    concluido = models.BooleanField(default=False)
    moedas = models.IntegerField()
    mudas = models.IntegerField()
    tempo = models.IntegerField()

    class Meta:
        db_table = 'Tarefas'

class PerfilRecompensas(models.Model):
    id_perfil = models.ForeignKey(
        Perfil,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_perfil'
    )
    id_recompensa = models.ForeignKey(
        Recompensas,
        on_delete=models.CASCADE,
        db_column='id_recompensa'
    )

    class Meta:
        db_table = 'PerfilRecompensas'