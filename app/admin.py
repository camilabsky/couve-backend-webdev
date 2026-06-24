from django.contrib import admin
from .models import Perfil, Tarefas, Recompensas, PerfilRecompensas


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'user')
    search_fields = ('nome', 'email')


@admin.register(Tarefas)
class TarefasAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'dificuldade', 'concluido', 'id_perfil', 'moedas', 'mudas')
    search_fields = ('titulo', 'tipo', 'horta')
    list_filter = ('concluido', 'tipo')


@admin.register(Recompensas)
class RecompensasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'preco')
    search_fields = ('nome', 'tipo')
    list_filter = ('tipo',)


@admin.register(PerfilRecompensas)
class PerfilRecompensasAdmin(admin.ModelAdmin):
    list_display = ('id_perfil', 'id_recompensa', 'data_resgate')
    list_filter = ('data_resgate',)