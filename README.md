# Couve Backend

Backend do App Couve — gamificação para hortas comunitárias.  
Django 4.x + Django REST Framework + JWT.

**Repositório:** https://github.com/camilabsky/ceubPI1/tree/main/backend

**Alunos:** Camila Bontempo · Enzo Nardelli · João Gabriel · Letícia de Souza

---

## Instalação

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/api/auth/login/` | Login (retorna token JWT) |
| POST | `/api/auth/refresh/` | Renovar token |
| CRUD | `/api/usuarios/` | Clientes / voluntários / gestores |
| CRUD | `/api/hortas/` | Hortas comunitárias |
| CRUD | `/api/loja/itens/` | Produtos da loja (controle de estoque) |
| POST | `/api/loja/compras/` | Registrar venda (desconta estoque e moedas) |
| GET  | `/api/loja/compras/relatorio/` | Relatório de vendas *(admin)* |

> Todas as rotas (exceto cadastro de usuário) exigem `Authorization: Bearer <token>`.

---

## Testes

```bash
python manage.py test apps.loja --verbosity=2
```
