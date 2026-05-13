# 🌿 Couve Backend API

Backend da plataforma **Couve** — sistema de gestão de hortas comunitárias com gamificação.  
Desenvolvido com **Django 4.x + Django REST Framework**.

---

## Contexto do Sistema

O Couve conecta voluntários a hortas comunitárias por meio de missões, recompensas e uma loja virtual. O sistema gerencia usuários (voluntários e gestores), hortas, missões, conquistas e um comércio interno baseado em moedas virtuais.

### Requisitos Funcionais
- Cadastro e autenticação de usuários (voluntários e gestores)
- CRUD de hortas comunitárias
- CRUD de itens da loja com controle de estoque
- Registro de compras/vendas com desconto de estoque e moedas
- Relatório de vendas por item
- Controle de missões e conquistas

### Requisitos Não Funcionais
- Autenticação via JWT (segurança)
- Validação de integridade no servidor (moedas e estoque verificados antes de persistir)
- API REST padronizada com DRF (manutenibilidade)
- Banco SQLite em desenvolvimento, compatível com PostgreSQL em produção (portabilidade)

---

## Estrutura do Projeto

```
backend/
├── core/               # Configurações, URLs raiz, WSGI
├── apps/
│   ├── usuarios/       # Modelo Usuario, CRUD, autenticação
│   ├── hortas/         # Modelo Horta, CRUD
│   ├── missoes/        # Missões e participações
│   ├── recompensas/    # Transações de moedas
│   ├── loja/           # Itens, vendas e relatórios
│   └── conquistas/     # Conquistas desbloqueadas
├── manage.py
└── requirements.txt
```

---

## Configuração e Execução

### Pré-requisitos
- Python 3.10+

### Instalação

```bash
# 1. Clone o repositório
git clone <URL_DO_REPO>
cd backend

# 2. Crie e ative o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Aplique as migrações
python manage.py migrate

# 5. Crie um superusuário (para acessar /admin/ e relatórios)
python manage.py createsuperuser

# 6. Inicie o servidor
python manage.py runserver
```

---

## Endpoints da API

### Autenticação
| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/api/auth/login/` | Obter token JWT |
| POST | `/api/auth/refresh/` | Renovar token JWT |

### Usuários (Clientes)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/usuarios/` | Listar usuários |
| POST | `/api/usuarios/` | Cadastrar usuário (público) |
| GET | `/api/usuarios/{id}/` | Detalhar usuário |
| PUT/PATCH | `/api/usuarios/{id}/` | Atualizar usuário |
| DELETE | `/api/usuarios/{id}/` | Remover usuário |

### Hortas
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/hortas/` | Listar hortas |
| POST | `/api/hortas/` | Criar horta |
| GET | `/api/hortas/{id}/` | Detalhar horta |
| PUT/PATCH | `/api/hortas/{id}/` | Atualizar horta |
| DELETE | `/api/hortas/{id}/` | Remover horta |

### Loja — Produtos (ItemLoja)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/loja/itens/` | Listar itens (use `?disponivel=true` para filtrar) |
| POST | `/api/loja/itens/` | Criar item com estoque |
| GET | `/api/loja/itens/{id}/` | Detalhar item |
| PUT/PATCH | `/api/loja/itens/{id}/` | Atualizar item / ajustar estoque |
| DELETE | `/api/loja/itens/{id}/` | Remover item |

### Loja — Vendas (Compras)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/loja/compras/` | Listar compras do usuário logado |
| POST | `/api/loja/compras/` | Registrar venda (desconta estoque e moedas) |
| GET | `/api/loja/compras/relatorio/` | Relatório de vendas *(admin)* |

#### Exemplo — Registrar venda
```json
POST /api/loja/compras/
Authorization: Bearer <token>

{
  "item": 1,
  "quantidade": 2
}
```
Resposta `201`:
```json
{
  "id": 1,
  "usuario": "joao",
  "item": 1,
  "item_nome": "Mudas de Alface",
  "quantidade": 2,
  "total_moedas": 20,
  "realizada_em": "2026-05-13T10:00:00Z"
}
```

#### Exemplo — Relatório de vendas
```json
GET /api/loja/compras/relatorio/
Authorization: Bearer <admin_token>

{
  "total_vendas": 42,
  "total_moedas_movimentadas": 630,
  "vendas_por_item": [
    {"item__nome": "Mudas de Alface", "qtd_vendida": 20, "receita_moedas": 300},
    {"item__nome": "Rúcula", "qtd_vendida": 15, "receita_moedas": 225}
  ]
}
```

---

## Controle de Estoque

Ao registrar uma compra (`POST /api/loja/compras/`), o sistema:
1. Verifica se o item está ativo e com estoque disponível
2. Verifica se o usuário possui moedas suficientes
3. Desconta `quantidade` do `ItemLoja.estoque`
4. Desconta `total_moedas` de `Usuario.moedas`
5. Persiste o registro de `Compra`

Se qualquer validação falhar, retorna `400 Bad Request` com mensagem descritiva.

---

## Testes

```bash
python manage.py test apps.loja --verbosity=2
```

10 testes cobrindo:
- CRUD de usuários
- CRUD de itens da loja
- Registro de vendas e desconto de estoque
- Validação de estoque insuficiente
- Validação de moedas insuficientes
- Relatório de vendas

---

## Diagrama de Domínio (resumo)

```
Usuario ──< ParticipacaoMissao >── Missao ──── Horta
   |                                              |
   └──< Compra >── ItemLoja ───────────────────── Horta
   |
   └──< ConquistaUsuario >── Conquista
   |
   └──< TransacaoMoeda
```

---

## Variáveis de Ambiente (`.env`)

```env
SECRET_KEY=sua-chave-secreta
DEBUG=True
ALLOWED_HOSTS=*
```

---

## Tecnologias

- Django 4.2
- Django REST Framework 3.14
- djangorestframework-simplejwt
- django-cors-headers
- SQLite (dev) / PostgreSQL (prod)
