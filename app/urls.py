from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('recompensas-api', views.RecompensasViewSet, basename='recompensas-api')


urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('', include(router.urls)),
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
    path("me/", views.me, name="me"),
    path("login/", views.login_page, name="login"),
    path("cadastro/", views.cadastro_page, name="cadastro"),
    path("logout/", views.logout_page, name="logout"),
    ]
