# Render CLI — conexão pelo PowerShell

CLI instalado em: `C:\Users\wesle\bin\render.exe`  
Conta: `weslensioliveira@gmail.com`  
Serviço: **FinancasPessoais** — `srv-d9hui8jtqb8s73a97d70`  
URL: https://financaspessoais-eloo.onrender.com

## CRITICAL — Dashboard antes de qualquer deploy

| Variável | Valor | Por quê |
|----------|-------|---------|
| `DATABASE_URL` | URL interna PostgreSQL | Sem isso → SQLite → `no such table: auth_user` |
| `PYTHON_VERSION` | `3.12.0` | Sem isso → Python 3.14 nos logs |
| **Start Command** | `./start.sh` | Sem migrate no startup → tabelas ausentes |

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

## Comandos rápidos

```powershell
# Novo terminal (PATH atualizado)
render --version

# Workspace (se necessário)
render workspace set tea-d9hufqmpbkes739pmek0 --confirm

# Conectar Shell (interativo — obrigatório; não funciona no shell do Cursor)
render ssh srv-d9hui8jtqb8s73a97d70 --confirm
```

> **Plano free:** `render jobs create` não está disponível. Use `render ssh` ou o **Shell** no [Dashboard Render](https://dashboard.render.com/web/srv-d9hui8jtqb8s73a97d70).

## Alternativa: Shell no navegador

Dashboard → **FinancasPessoais** → aba **Shell** → cole os comandos abaixo.

## Fix imediato no Shell remoto

```bash
# 1. Verificar variáveis
echo "DATABASE_URL=${DATABASE_URL:-NAO_DEFINIDA}"
python --version

# 2. Migrar e criar admin
python manage.py migrate --noinput
export DJANGO_SUPERUSER_USERNAME=Admin
export DJANGO_SUPERUSER_PASSWORD=170691
export DJANGO_SUPERUSER_EMAIL=admin@financaspessoal.local
python manage.py ensure_superuser
```

Teste: https://financaspessoais-eloo.onrender.com/admin/login/

## Variáveis no Dashboard (persistir)

No Render → **FinancasPessoais** → **Environment**:

| Chave | Valor |
|-------|--------|
| `DATABASE_URL` | URL interna do PostgreSQL |
| `PYTHON_VERSION` | `3.12.0` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(string longa)* |
| `DJANGO_SUPERUSER_USERNAME` | `Admin` |
| `DJANGO_SUPERUSER_PASSWORD` | `170691` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@financaspessoal.local` |

**Start Command:** `./start.sh`

## Logs

```powershell
render logs srv-d9hui8jtqb8s73a97d70
```

Procure por `[start.sh] Migrate concluído` ou `[deploy] migrate concluído`.
