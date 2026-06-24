# Couve Backend (Django)

Sistema web com API REST para gestão de tarefas e recompensas comunitárias. O projeto inclui autenticação por sessão (interface web), API protegida e relatórios administrativos.

## Stack

- Python 3.11+
- Django 6
- Django REST Framework
- SimpleJWT
- SQLite

## Funcionalidades principais

- Landing pública e autenticação de usuários.
- Páginas privadas protegidas por login: home, tarefas, recompensas e perfil.
- Fluxo de tarefas: aceitar e concluir.
- Fluxo de recompensas: listar e resgatar com regra de saldo e estoque.
- API REST de recompensas com leitura pública e escrita protegida por JWT.
- Perfil admin com relatórios:
  - Relatório 1: recompensas resgatadas por usuário.
  - Relatório 2: tarefas concluídas por semana, ranking de usuários e detalhamento por usuário.

## Como rodar o projeto

## 1) Clonar repositório

```bash
git clone https://github.com/camilabsky/couve-backend-webdev.git
cd couve-backend-webdev
```

## 2) Criar e ativar ambiente virtual

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se houver bloqueio de script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows (CMD)

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

## 3) Instalar dependências

```bash
pip install -r requirements.txt
pip install djangorestframework-simplejwt
```

## 4) Aplicar migrações

```bash
python manage.py migrate
```

## 5) Iniciar servidor

```bash
python manage.py runserver 127.0.0.1:8000
```

## 6) Validar configuração

```bash
python manage.py check
```

## Rotas web

- Landing: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Home: http://127.0.0.1:8000/home/
- Tarefas: http://127.0.0.1:8000/tarefas/
- Recompensas: http://127.0.0.1:8000/recompensas/
- Perfil: http://127.0.0.1:8000/perfil/
- Admin Django: http://127.0.0.1:8000/admin/

## API REST

## Recompensas (ViewSet)

Base: `GET /recompensas-api/`

Regras atuais:

- `GET/HEAD/OPTIONS`: público.
- `POST/PUT/PATCH/DELETE`: protegido por JWT.

## Endpoints auxiliares legados

Disponíveis em rotas como:

- `/minhas_tarefas`
- `/tarefas_concluidas`
- `/minhas_moedas`
- `/minhas_mudas`
- `/minhas_recompensas`
- `/tarefas_disponiveis`
- `/aceitar_tarefa`
- `/concluir_tarefa`
- `/recompensas_disponiveis`
- `/resgatar_recompensa`

## Regras de negócio importantes

- Usuário só conclui tarefa que aceitou.
- Recompensa só pode ser resgatada com saldo suficiente.
- Recompensa só pode ser resgatada com estoque disponível.
- Edição de perfil permite apenas campos seguros (nome e email).

## Relatórios administrativos

Disponíveis no perfil do superusuário (`/perfil/`):

- Relatório 1: usuários com lista das recompensas resgatadas.
- Relatório 2:
  - número de tarefas cumpridas por semana;
  - ranking de usuários por tarefas concluídas;
  - detalhamento de quem cumpriu quais tarefas.

## Estrutura resumida

- `app/models.py`: entidades de domínio.
- `app/views.py`: regras de negócio, pages e endpoints.
- `app/urls.py`: rotas web e API da app.
- `horta/urls.py`: roteamento principal e JWT.
- `app/templates/app/`: interface HTML.

## Solução de problemas rápida

- `ERR_CONNECTION_REFUSED`:
  - confirme que o servidor está rodando com `python manage.py runserver`.

- erro ao ativar venv com `python .venv\Scripts\activate.bat`:
  - não use `python` para ativação;
  - use `.\.venv\Scripts\activate.bat` (CMD) ou `.\.venv\Scripts\Activate.ps1` (PowerShell).




