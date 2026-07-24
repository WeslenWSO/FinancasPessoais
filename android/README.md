# App Android — Finanças Pessoais

App nativo em **Kotlin + Jetpack Compose** que consome a API REST do backend Django.

## Requisitos

- Android Studio Ladybug (2024.2+) ou newer
- JDK 17
- Backend Django rodando e acessível na rede

## 1. Subir o backend

```powershell
cd ..
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

> Use `0.0.0.0:8000` para aceitar conexões do emulador e do celular na mesma rede Wi‑Fi.

## 2. Abrir o projeto

1. Abra o Android Studio
2. **File → Open** → selecione a pasta `android/`
3. Aguarde o Gradle sync

## 3. URL do servidor

| Ambiente | URL padrão |
|----------|------------|
| Emulador Android | `http://10.0.2.2:8000/` |
| Celular físico (mesma rede) | `http://SEU_IP_LOCAL:8000/` |

Na tela de login, toque em **Configurar servidor** para alterar a URL.

## 4. Login

Use o mesmo usuário do sistema web, por exemplo:

- Usuário: `Paulo`
- Senha: `170691`

## 5. Executar

- Emulador: clique em **Run** (▶)
- APK debug: `./gradlew assembleDebug` (dentro de `android/`)

## Telas do app

- **Início** — dashboard (KPIs + resumo 6 meses)
- **Contas** — lista de contas
- **Receitas** / **Despesas** — lançamentos
- **Mais** — cartões e previsão 12 meses

## API utilizada

- `POST /api/auth/token/` — login JWT
- `GET /api/v1/dashboard/`
- `GET /api/v1/contas/`, `/receitas/`, `/despesas/`, etc.

Documentação completa: http://127.0.0.1:8000/api/docs/
