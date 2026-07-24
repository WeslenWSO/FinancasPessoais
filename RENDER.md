# Deploy no Render — checklist

## Settings do Web Service

| Campo | Valor |
|-------|--------|
| **Root Directory** | *(vazio)* |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| **Start Command** | `gunicorn wsgi:application --bind 0.0.0.0:$PORT` |
| **PYTHON_VERSION** | `3.12.0` |

## Variáveis de ambiente

| Chave | Valor |
|-------|--------|
| `DEBUG` | `False` |
| `SECRET_KEY` | *(gerar string longa)* |
| `DATABASE_URL` | *(URL interna do Postgres Render)* |

## Deploy

1. Confirme que o commit é **`508559a`** ou mais recente (não `c4623a5`)
2. **Manual Deploy → Deploy latest commit**
3. Logs devem mostrar `Listening at: http://0.0.0.0:XXXX`

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `No module named 'FinancasPessoais'` | Commit antigo ou Start Command errado | Deploy latest + use `gunicorn wsgi:application` |
| `gunicorn: command not found` | Build Command vazio | Instalar `pip install -r requirements.txt` |
| `Port scan timeout` | App crashou antes de subir | Corrigir erro de import acima |

## Primeiro login

Banco de produção vazio → crie conta em `/register/` ou `createsuperuser` no Shell.
