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
