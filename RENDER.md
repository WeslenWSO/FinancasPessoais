# Deploy no Render — checklist

## CRITICAL — configure antes do deploy

Serviço manual: **FinancasPessoais** — https://financaspessoais-eloo.onrender.com

| # | Item | Valor obrigatório | Se faltar |
|---|------|-------------------|-----------|
| 1 | **DATABASE_URL** | URL interna do PostgreSQL | SQLite ephemeral → `no such table: auth_user` |
| 2 | **PYTHON_VERSION** | `3.12.0` | Render usa Python 3.14 (incompatível) |
| 3 | **Start Command** | `./start.sh` | migrate não roda → tabelas ausentes |
| 4 | **DEBUG** | `False` | *(auto quando RENDER detectado)* |
| 5 | **SECRET_KEY** | string longa aleatória | inseguro |

> Sem `DATABASE_URL`, o app ainda sobe com SQLite e roda migrate no startup (fallback), mas **os dados somem a cada deploy**. PostgreSQL é obrigatório para produção real.

## Settings do Web Service (FinancasPessoais)

| Campo | Valor |
|-------|--------|
| **Root Directory** | *(vazio)* |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| **Start Command** | `./start.sh` |
| **PYTHON_VERSION** | `3.12.0` |

Alternativa ao Start Command (se `./start.sh` falhar por permissão):

```bash
python manage.py migrate --noinput && python manage.py ensure_superuser || true && gunicorn wsgi:application --bind 0.0.0.0:$PORT
```

## PostgreSQL (obrigatório para produção)

1. **New → PostgreSQL** (Free) → nome ex.: `financas-db`
2. Copie a **Internal Database URL**
3. No Web Service **FinancasPessoais** → **Environment** → adicione:
   - `DATABASE_URL` = URL interna do Postgres

## Outras variáveis de ambiente

| Chave | Valor |
|-------|--------|
| `DEBUG` | `False` |
| `SECRET_KEY` | *(gerar string longa)* |
| `PYTHON_VERSION` | `3.12.0` |
| `DJANGO_SUPERUSER_USERNAME` | `Admin` |
| `DJANGO_SUPERUSER_PASSWORD` | *(sua senha — ex.: 170691)* |
| `DJANGO_SUPERUSER_EMAIL` | `admin@financaspessoal.local` |

> Defina `DJANGO_SUPERUSER_*` no painel do Render (Environment). **Não** commite a senha no Git.

## Criar admin manualmente (Render Shell)

Se preferir criar agora, no **Shell** do serviço:

```bash
export DJANGO_SUPERUSER_USERNAME=Admin
export DJANGO_SUPERUSER_PASSWORD=170691
export DJANGO_SUPERUSER_EMAIL=admin@financaspessoal.local
python manage.py migrate --noinput
python manage.py ensure_superuser
```

Ou interativo:

```bash
python manage.py createsuperuser
```

## Deploy

1. Confirme o checklist CRITICAL acima
2. **Manual Deploy → Deploy latest commit**
3. Logs devem mostrar:
   - `[start.sh] Executando migrate...`
   - `Applying migrations...`
   - `[deploy] migrate concluído`
   - `Listening at: http://0.0.0.0:XXXX`

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `no such table: auth_user` | Sem Postgres / migrate não rodou | `DATABASE_URL` + Start Command com migrate + redeploy |
| `No module named 'FinancasPessoais'` | Start Command errado | Use `gunicorn wsgi:application` |
| `gunicorn: command not found` | Build Command vazio | `pip install -r requirements.txt` |
| Python 3.14 nos logs | `PYTHON_VERSION` não definido | Defina `3.12.0` no Environment |

## Primeiro login

Após migrate OK → `/admin/login/` ou `/register/` ou `python manage.py createsuperuser` no Shell.
