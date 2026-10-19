# Bot Vagas Freelance 🤖

Bot Telegram que monitora vagas de desenvolvimento no **Trampos.co** e **99Freelas** e envia alertas em tempo real.

## 🚀 Deploy no Railway (Grátis)

### 1. Criar repositório no GitHub
```bash
cd /home/arthur/freelance_repos/bot-vagas-freelance
git init
git add .
git commit -m "Initial commit: Bot Vagas Freelance"
gh repo create bot-vagas-freelance --public --source=. --remote=origin --push
```

### 2. Deploy no Railway
1. Acesse [railway.app](https://railway.app)
2. Conecte GitHub → Selecione `bot-vagas-freelance`
3. Railway detecta Dockerfile automaticamente
4. Em **Variables**, adicione:
   - `TELEGRAM_TOKEN` = token do @BotFather
   - `TELEGRAM_CHAT_ID` = seu chat_id (use @userinfobot)
   - `CHECK_INTERVAL_MINUTES` = 60 (opcional)

### 3. Deploy automático
Railway builda a imagem Docker e deploya. O bot inicia sozinho.

## 📋 Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot, mostra ajuda |
| `/status` | Mostra status (vagas vistas, última verificação) |
| `/check` | Verificação manual agora |
| `/help` | Ajuda |

## 📦 Fontes Monitoradas

| Fonte | Engine | Status |
|-------|--------|--------|
| **Trampos.co** | Playwright | ✅ Funcionando |
| **99Freelas** | Playwright | ✅ Funcionando |

## ⚙️ Configuração

### Variáveis de ambiente (.env)
```bash
TELEGRAM_TOKEN=seu_token_do_botfather
TELEGRAM_CHAT_ID=seu_chat_id
CHECK_INTERVAL_MINUTES=60
```

### Obter TELEGRAM_TOKEN
1. Fale com [@BotFather](https://t.me/BotFather)
2. `/newbot` → siga instruções
3. Copie o token

### Obter TELEGRAM_CHAT_ID
1. Fale com [@userinfobot](https://t.me/userinfobot)
2. Copie o `Id` retornado

## 🏗️ Arquitetura

```
main.py                 # Entry point, Telegram bot + scheduler
├── fetch_trampos()     # Playwright scraper Trampos.co
├── fetch_99freelas()   # Playwright scraper 99Freelas
├── check_new_vagas()   # Dedup + keywords matching
├── scheduled_check()   # APScheduler job (a cada 60 min)
└── Telegram handlers   # /start, /status, /check
```

## 🔍 Keywords Monitoradas

- **Tech stack**: python, django, fastapi, flask, react, node, go, java, c#, react native, flutter
- **Cargos**: analista, especialista, sênior, pleno, júnior, tech lead, gerente, arquiteto
- **Stack**: react, node, python, django, fastapi, flask, go, java, .net, mobile, flutter
- **DevOps/Cloud**: docker, kubernetes, aws, azure, terraform, ci/cd
- **Dados/IA**: machine learning, dados, analytics, bi, power bi
- **Freelance terms**: automação, scraping, bot, whatsapp, integração, landing page, saas

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt
playwright install chromium

# Rodar local
cp .env.example .env
# edite .env com suas credenciais
python main.py
```

## 📊 Monitoramento

- Logs: `railway logs` ou dashboard Railway
- Health check: `/status` no bot
- Verificação manual: `/check` no bot

## 💰 Custos

| Recurso | Custo |
|---------|-------|
| Railway (Hobby) | **Grátis** (500h/mês) |
| Playwright/Chromium | Incluído no container |
| Telegram Bot API | Grátis |

## 📝 Licença

MIT - Livre para uso comercial e pessoal.