# Deploy no Render — checklist

## Settings do Web Service

| Campo | Valor |
|-------|--------|
| **Root Directory** | *(vazio)* |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| **Start Command** | `python manage.py migrate --noinput && gunicorn wsgi:application --bind 0.0.0.0:$PORT` |
| **PYTHON_VERSION** | `3.12.0` |

## PostgreSQL (obrigatório)

1. **New → PostgreSQL** (Free) → nome ex.: `financas-db`
2. Copie a **Internal Database URL**
3. No Web Service → **Environment** → adicione:
   - `DATABASE_URL` = URL interna do Postgres

Sem `DATABASE_URL`, o Django usa SQLite e as tabelas não existem → erro `no such table: auth_user`.

## Outras variáveis

| Chave | Valor |
|-------|--------|
| `DEBUG` | `False` |
| `SECRET_KEY` | *(gerar string longa)* |

## Deploy

1. **Manual Deploy → Deploy latest commit**
2. Logs devem mostrar `Applying migrations...` e `Listening at: http://0.0.0.0:XXXX`

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `no such table: auth_user` | Sem Postgres / migrate não rodou | Criar `DATABASE_URL` + redeploy |
| `No module named 'FinancasPessoais'` | Start Command errado | Use `gunicorn wsgi:application` |
| `gunicorn: command not found` | Build Command vazio | `pip install -r requirements.txt` |
| Python 3.14 nos logs | `PYTHON_VERSION` não definido | Defina `3.12.0` |

## Primeiro login

Após migrate OK → `/register/` ou `python manage.py createsuperuser` no Shell.
