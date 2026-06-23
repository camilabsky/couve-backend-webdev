# Couve Backend (Django)

Projeto Django com interface web e endpoints de API, incluindo autenticacao JWT.

## Requisitos

- Python 3.11+ (recomendado)
- Git (opcional)

Dependencias principais:
- Django
- djangorestframework
- djangorestframework-simplejwt

## 1) Clonar o projeto

```bash
git clone https://github.com/camilabsky/couve-backend-webdev.git
cd couve-backend-webdev
```

Se voce ja esta com o projeto local, pule este passo.

## 2) Criar e ativar ambiente virtual

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se aparecer bloqueio de script no PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows (CMD)

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

## 3) Instalar dependencias

```bash
pip install -r requirements.txt
pip install djangorestframework-simplejwt
```

Observacao: o projeto usa JWT, entao a biblioteca simplejwt precisa estar instalada.

## 4) Aplicar migracoes

```bash
python manage.py migrate
```

## 5) Criar superusuario (opcional, recomendado)

```bash
python manage.py createsuperuser
```

## 6) Iniciar servidor

```bash
python manage.py runserver 127.0.0.1:8000
```

Abrir no navegador:
- Landing: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Admin: http://127.0.0.1:8000/admin/


## 10) Solucao de problemas rapida

- Erro de conexao no navegador (ERR_CONNECTION_REFUSED):
  - Verifique se o servidor esta rodando com `python manage.py runserver`.

- Erro ao ativar venv com `python .venv\Scripts\activate.bat`:
  - Nao use `python` para ativar.
  - Use diretamente `.\.venv\Scripts\activate.bat` (CMD) ou `.\.venv\Scripts\Activate.ps1` (PowerShell).


