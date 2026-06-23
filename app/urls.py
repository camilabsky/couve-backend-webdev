from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('tarefas/', views.tarefas_page, name='tarefas'),
    path('tarefas/<int:tarefa_id>/aceitar/', views.aceitar_tarefa_page, name='aceitar_tarefa_page'),
    path('tarefas/<int:tarefa_id>/concluir/', views.concluir_tarefa_page, name='concluir_tarefa_page'),
    path('recompensas/', views.recompensas_page, name='recompensas'),
    path('recompensas/<int:recompensa_id>/resgatar/', views.resgatar_recompensa_page, name='resgatar_recompensa_page'),
    path('perfil/', views.perfil_page, name='perfil'),
    path('minhas_tarefas', views.minhas_tarefas),
    path('tarefas_concluidas', views.tarefas_concluidas),
    path('minhas_moedas', views.minhas_moedas),
    path('minhas_mudas', views.minhas_mudas),
    path('minhas_recompensas', views.minhas_recompensas),
    path('concluir_tarefa', views.concluir_tarefa),
    path('tarefas_disponiveis', views.tarefas_disponiveis),
    path('aceitar_tarefa', views.aceitar_tarefa),
    path('recompensas_disponiveis', views.recompensas_disponiveis),
    path('resgatar_recompensa', views.resgatar_recompensa),
]