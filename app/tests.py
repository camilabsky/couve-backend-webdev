from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import Perfil, Tarefas, Recompensas, PerfilRecompensas

User = get_user_model()


class PerfilModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='maria123',
            email='maria@email.com',
            password='senha1234'
        )

    def test_criacao_perfil(self):
        perfil = Perfil.objects.create(
            user=self.user,
            nome='Maria Silva',
            email='maria@email.com'
        )
        self.assertEqual(perfil.nome, 'Maria Silva')
        self.assertEqual(perfil.email, 'maria@email.com')

    def test_perfil_vinculado_ao_user(self):
        perfil = Perfil.objects.create(
            user=self.user,
            nome='Maria Silva',
            email='maria@email.com'
        )
        self.assertEqual(perfil.user, self.user)

    def test_email_unico(self):
        Perfil.objects.create(
            user=self.user,
            nome='Maria Silva',
            email='maria@email.com'
        )
        user2 = User.objects.create_user(
            username='joao99',
            email='joao@email.com',
            password='senha1234'
        )
        with self.assertRaises(Exception):
            Perfil.objects.create(
                user=user2,
                nome='Joao',
                email='maria@email.com'
            )


class TarefasModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='carlos77',
            email='carlos@email.com',
            password='senha1234'
        )
        self.perfil = Perfil.objects.create(
            user=self.user,
            nome='Carlos',
            email='carlos@email.com'
        )

    def test_tarefa_criada_sem_dono(self):
        tarefa = Tarefas.objects.create(
            titulo='Regar plantas',
            tipo='Rega',
            dificuldade=1,
            horta='Horta Central',
            descricao='Regar todas as plantas da horta',
            moedas=50,
            mudas=2,
            tempo=30
        )
        self.assertIsNone(tarefa.id_perfil)
        self.assertFalse(tarefa.concluido)

    def test_aceitar_tarefa(self):
        tarefa = Tarefas.objects.create(
            titulo='Plantar tomate',
            tipo='Plantio',
            dificuldade=2,
            horta='Horta Norte',
            descricao='Plantar mudas de tomate',
            moedas=100,
            mudas=5,
            tempo=60
        )
        tarefa.id_perfil = self.perfil
        tarefa.save(update_fields=['id_perfil'])
        self.assertEqual(tarefa.id_perfil, self.perfil)

    def test_concluir_tarefa(self):
        tarefa = Tarefas.objects.create(
            titulo='Adubar solo',
            tipo='Manutencao',
            dificuldade=3,
            horta='Horta Sul',
            descricao='Adubar o solo da horta',
            id_perfil=self.perfil,
            moedas=150,
            mudas=0,
            tempo=45
        )
        tarefa.concluido = True
        tarefa.data_conclusao = timezone.now()
        tarefa.save(update_fields=['concluido', 'data_conclusao'])
        self.assertTrue(tarefa.concluido)
        self.assertIsNotNone(tarefa.data_conclusao)


class SaldoTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='ana456',
            email='ana@email.com',
            password='senha1234'
        )
        self.perfil = Perfil.objects.create(
            user=self.user,
            nome='Ana',
            email='ana@email.com'
        )
        self.recompensa = Recompensas.objects.create(
            nome='Cesta de Vegetais',
            descricao='Cesta com vegetais frescos',
            preco=200,
            tipo='Produtos',
            src='https://images.unsplash.com/foto.jpg'
        )

    def test_saldo_com_tarefas_concluidas(self):
        Tarefas.objects.create(
            titulo='Tarefa 1',
            tipo='Rega',
            dificuldade=1,
            horta='Horta A',
            descricao='Desc',
            id_perfil=self.perfil,
            concluido=True,
            moedas=300,
            mudas=0,
            tempo=20
        )
        from .views import get_profile_balance
        saldo = get_profile_balance(self.perfil)
        self.assertEqual(saldo, 300)

    def test_saldo_diminui_apos_resgate(self):
        Tarefas.objects.create(
            titulo='Tarefa 2',
            tipo='Plantio',
            dificuldade=2,
            horta='Horta B',
            descricao='Desc',
            id_perfil=self.perfil,
            concluido=True,
            moedas=300,
            mudas=0,
            tempo=30
        )
        PerfilRecompensas.objects.create(
            id_perfil=self.perfil,
            id_recompensa=self.recompensa,
            data_resgate=timezone.now()
        )
        from .views import get_profile_balance
        saldo = get_profile_balance(self.perfil)
        self.assertEqual(saldo, 100)

    def test_saldo_zerado_sem_tarefas(self):
        from .views import get_profile_balance
        saldo = get_profile_balance(self.perfil)
        self.assertEqual(saldo, 0)


class RecompensasModelTest(TestCase):

    def test_criacao_recompensa(self):
        recompensa = Recompensas.objects.create(
            nome='Kit de Ferramentas',
            descricao='Kit com pá, rastelo e luvas',
            preco=500,
            tipo='Ferramentas',
            src='https://images.unsplash.com/foto2.jpg'
        )
        self.assertEqual(recompensa.nome, 'Kit de Ferramentas')
        self.assertEqual(recompensa.preco, 500)

    def test_resgate_vincula_perfil(self):
        user = User.objects.create_user(
            username='pedro11',
            email='pedro@email.com',
            password='senha1234'
        )
        perfil = Perfil.objects.create(
            user=user,
            nome='Pedro',
            email='pedro@email.com'
        )
        recompensa = Recompensas.objects.create(
            nome='Sacola Ecologica',
            descricao='Sacola reutilizavel',
            preco=100,
            tipo='Acessorios',
            src='https://images.unsplash.com/foto3.jpg'
        )
        resgate = PerfilRecompensas.objects.create(
            id_perfil=perfil,
            id_recompensa=recompensa,
            data_resgate=timezone.now()
        )
        self.assertEqual(resgate.id_perfil, perfil)
        self.assertEqual(resgate.id_recompensa, recompensa)


class LoginCadastroTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_cadastro_usuario_novo(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'novousuario',
            'email': 'novo@email.com',
            'nome_completo': 'Usuario Novo',
            'password': 'senha1234',
            'password_confirm': 'senha1234',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='novousuario').exists())

    def test_cadastro_senha_diferente(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'outrouser',
            'email': 'outro@email.com',
            'nome_completo': 'Outro',
            'password': 'senha1234',
            'password_confirm': 'senhaerrada',
        })
        self.assertFalse(User.objects.filter(username='outrouser').exists())

    def test_login_valido(self):
        User.objects.create_user(
            username='teste99',
            email='teste@email.com',
            password='senha1234'
        )
        response = self.client.post(reverse('login'), {
            'username': 'teste99',
            'password': 'senha1234',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_senha_errada(self):
        User.objects.create_user(
            username='teste88',
            email='teste88@email.com',
            password='senha1234'
        )
        response = self.client.post(reverse('login'), {
            'username': 'teste88',
            'password': 'senhaerrada',
        })
        self.assertEqual(response.status_code, 200)

    def test_pagina_home_sem_login_redireciona(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)