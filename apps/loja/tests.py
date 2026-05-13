from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario
from apps.hortas.models import Horta
from apps.loja.models import ItemLoja, Compra


class UsuarioCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create_superuser(
            username='admin', password='admin1234', email='admin@test.com'
        )
        self.client.force_authenticate(user=self.admin)

    def test_cadastrar_usuario(self):
        """Deve criar novo usuário via POST /api/usuarios/."""
        resp = self.client.post('/api/usuarios/', {
            'username': 'joao',
            'email': 'joao@test.com',
            'password': 'senha1234',
            'tipo': 'voluntario',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(username='joao').exists())

    def test_listar_usuarios(self):
        """GET /api/usuarios/ deve retornar lista."""
        resp = self.client.get('/api/usuarios/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_detalhar_usuario(self):
        """GET /api/usuarios/<id>/ deve retornar o usuário."""
        resp = self.client.get(f'/api/usuarios/{self.admin.pk}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'admin')


class ItemLojaCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gestor = Usuario.objects.create_user(
            username='gestor', password='senha1234', email='gestor@test.com', tipo='gestor'
        )
        self.horta = Horta.objects.create(
            nome='Horta Teste', endereco='Rua A, 1', gestor=self.gestor
        )
        self.client.force_authenticate(user=self.gestor)

    def test_criar_item(self):
        """POST /api/loja/itens/ deve criar item com estoque."""
        resp = self.client.post('/api/loja/itens/', {
            'horta': self.horta.pk,
            'nome': 'Mudas de Alface',
            'preco_moedas': 10,
            'estoque': 50,
            'ativo': True,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['estoque'], 50)

    def test_listar_itens(self):
        """GET /api/loja/itens/ deve retornar lista de itens."""
        resp = self.client.get('/api/loja/itens/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_atualizar_estoque(self):
        """PATCH /api/loja/itens/<id>/ deve atualizar estoque."""
        item = ItemLoja.objects.create(
            horta=self.horta, nome='Cenoura', preco_moedas=5, estoque=20
        )
        resp = self.client.patch(f'/api/loja/itens/{item.pk}/', {'estoque': 35}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.estoque, 35)


class RegistroVendasTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gestor = Usuario.objects.create_user(
            username='gestor2', password='senha1234', email='gestor2@test.com', tipo='gestor'
        )
        self.comprador = Usuario.objects.create_user(
            username='comprador', password='senha1234', email='comprador@test.com',
            tipo='voluntario', moedas=100
        )
        self.horta = Horta.objects.create(
            nome='Horta B', endereco='Rua B, 2', gestor=self.gestor
        )
        self.item = ItemLoja.objects.create(
            horta=self.horta, nome='Rúcula', preco_moedas=15, estoque=10, ativo=True
        )

    def test_registrar_compra(self):
        """POST /api/loja/compras/ deve registrar venda e descontar estoque."""
        self.client.force_authenticate(user=self.comprador)
        resp = self.client.post('/api/loja/compras/', {
            'item': self.item.pk,
            'quantidade': 2,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['total_moedas'], 30)

        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque, 8)  # 10 - 2

        self.comprador.refresh_from_db()
        self.assertEqual(self.comprador.moedas, 70)  # 100 - 30

    def test_compra_estoque_insuficiente(self):
        """Compra com quantidade acima do estoque deve retornar 400."""
        self.client.force_authenticate(user=self.comprador)
        resp = self.client.post('/api/loja/compras/', {
            'item': self.item.pk,
            'quantidade': 99,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_compra_moedas_insuficientes(self):
        """Compra sem moedas suficientes deve retornar 400."""
        self.comprador.moedas = 5
        self.comprador.save()
        self.client.force_authenticate(user=self.comprador)
        resp = self.client.post('/api/loja/compras/', {
            'item': self.item.pk,
            'quantidade': 1,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorio_vendas(self):
        """GET /api/loja/compras/relatorio/ deve retornar resumo de vendas para admin."""
        admin = Usuario.objects.create_superuser(
            username='superadmin', password='admin1234', email='superadmin@test.com'
        )
        self.client.force_authenticate(user=admin)
        resp = self.client.get('/api/loja/compras/relatorio/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_vendas', resp.data)
        self.assertIn('total_moedas_movimentadas', resp.data)
        self.assertIn('vendas_por_item', resp.data)
