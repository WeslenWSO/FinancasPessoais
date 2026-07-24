# Finanças Pessoais — Django

Sistema de finanças pessoais multi-usuário, portado do HTML original (`financas-pessoais.html`).

## Funcionalidades

- Dashboard com KPIs, gráficos (Chart.js), faturas e orçamento
- CRUD: Contas, Cartões, Categorias, Receitas, Despesas, Investimentos, Bens, Orçamento
- Previsão financeira (12 meses)
- Backup export/import JSON (compatível com formato HTML)
- API REST com JWT para app Android

## Requisitos

- Python 3.11+
- pip

## Instalação

```bash
cd FinancasPessoal
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Acesse: http://127.0.0.1:8000/

> Para o **app Android** (emulador ou celular), use `runserver 0.0.0.0:8000` — veja [android/README.md](android/README.md).

## App Android

Projeto nativo em Kotlin + Jetpack Compose na pasta [`android/`](android/).

```text
android/          → abrir no Android Studio
android/README.md → instruções de build e URL do servidor
```

Login no app usa a mesma conta da web (JWT). URL padrão no emulador: `http://10.0.2.2:8000/`

## API

- Documentação Swagger: http://127.0.0.1:8000/api/docs/
- Token JWT: `POST /api/auth/token/` com `username` e `password`
- Refresh: `POST /api/auth/token/refresh/`
- Recursos: `/api/v1/contas/`, `/api/v1/cartoes/`, `/api/v1/categorias/`, etc.
- Calculados: `/api/v1/dashboard/?mes=YYYY-MM`, `/api/v1/previsao/`, `/api/v1/saldo/`
- Backup: `GET /api/v1/backup/export/`, `POST /api/v1/backup/import/`

## Testes

```bash
python manage.py test financas
```

## Estrutura

- `financas/models.py` — modelos de dados
- `financas/services/` — lógica de negócio (faturas, saldo, previsão)
- `financas/views/` — interface web
- `financas/api/` — REST API (DRF)
- `financas/templates/` — templates Django + HTMX

## Deploy no Render (GitHub → Render)

Fluxo: **Cursor** edita o código → **git push** para GitHub → **Render** faz deploy automático.

### 1. Conectar GitHub ao Render

1. Crie conta em [render.com](https://render.com)
2. Conecte sua conta **GitHub**
3. Autorize o repositório `WeslenWSO/FinancasPessoais`
4. **New → Blueprint** e selecione o repo (usa o arquivo [`render.yaml`](render.yaml))

### 2. O que o Render cria

- **Web Service** `financas-pessoais` — Django com Gunicorn
- **PostgreSQL** `financas-db` — banco persistente (não use SQLite em produção)

Comando de start:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. Variáveis de ambiente (automáticas via Blueprint)

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Gerada automaticamente |
| `DEBUG` | `False` |
| `DATABASE_URL` | Vinculada ao Postgres |
| `RENDER_EXTERNAL_HOSTNAME` | Definida pelo Render (ALLOWED_HOSTS) |

Opcionais no painel do Render:

- `CORS_ALLOWED_ORIGINS` — URLs extras separadas por vírgula
- `CSRF_TRUSTED_ORIGINS` — ex.: `https://financas-pessoais.onrender.com`

### 4. Fluxo no Cursor

```powershell
git add .
git commit -m "sua mensagem"
git push origin main
```

Cada push na branch `main` dispara um novo deploy. Acompanhe logs no **Render Dashboard**.

### 5. Pós-deploy

1. Crie um superusuário via **Render Shell**:
   ```bash
   python manage.py createsuperuser
   ```
2. Acesse a URL: `https://financas-pessoais.onrender.com`
3. No **app Android**, use **Configurar servidor** com a URL HTTPS do Render

> **Plano free:** o serviço dorme após inatividade; a primeira requisição pode levar ~50s.

