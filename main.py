"""
Bot Telegram - Vagas Freelance (Trampos + 99Freelas)
Monitora vagas de desenvolvimento e envia alertas no Telegram.

Stack: python-telegram-bot, Playwright, APScheduler, Render (deploy gratis)
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

import aiohttp
from aiohttp import web
from playwright.async_api import async_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))

# Keywords para vagas tech (foco dev)
KEYWORDS = [
    "python", "desenvolvedor", "programador", "backend", "frontend", "api",
    "django", "fastapi", "flask", "react", "node", "javascript", "typescript",
    "golang", "java", "csharp", "dotnet", "mobile", "react native", "flutter",
    "ios", "android", "fullstack", "devops", "dados", "machine learning",
    "inteligência artificial", "ia generativa", "web", "sistema", "aplicativo",
    "app", "site", "e-commerce", "marketplace", "saas", "shopify",
    "landing page", "wordpress", "php", "laravel", "crm", "erp", "automação",
    "scraping", "bot", "whatsapp", "integração", "landing page", "seo",
    "google ads", "facebook ads", "tráfego pago", "analytics", "bi",
    "power bi", "tableau", "salesforce", "aws", "azure", "docker", "kubernetes",
    "microserviços", "arquitetura", "clean code", "tdd", "agile", "scrum",
    "golang", "csharp", "dotnet", "salesforce", "aws", "azure", "docker",
    "kubernetes", "microserviços", "arquitetura", "clean code", "tdd", "agile", "scrum",
    "analista", "especialista", "sênior", "senior", "pleno", "júnior", "junior",
    "lider", "líder", "tech lead", "gerente", "gerência", "coordenador",
    "coordenacao", "arquiteto", "arquitetura", "consultor", "consultoria",
    "planejamento", "estratégico", "estratégia", "atendimento", "suporte",
    "helpdesk", "service desk", "bdr", "sdr", "vendas", "comercial",
    "pre-sales", "pos-vendas", "customer success", "cs", "account manager",
    "account", "performance", "mídia", "midia", "marketing digital",
    "growth", "aquisição", "retencao", "retention"
]

# Configuração das fontes
SOURCES = [
    {
        "id": "trampos",
        "name": "Trampos.co",
        "url": "https://trampos.co/oportunidades",
        "engine": "playwright",
        "selectors": {
            "container": ".opportunity-box",
            "title": "h4",
            "url": "a.ember-view.inner",
            "company": ".info h5",
            "location": ".location",
            "type": ".type",
            "tags": ".when .label",
            "featured": ".when .label.featured"
        }
    },
    {
        "id": "freelas99",
        "name": "99Freelas",
        "url": "https://www.99freelas.com.br/projects?category=development",
        "engine": "playwright",
        "selectors": {
            "container": "li.result-item",
            "title": "h1.title a",
            "url": "h1.title a",
            "category": "p.item-text.information",
            "description": "div.item-text.description.formatted-text",
            "posted": "b.datetime",
            "proposals": "p.item-text.information b"
        }
    }
]

KEYWORDS_LOWER = [kw.lower() for kw in KEYWORDS]
seen_vagas = set()


async def fetch_trampos() -> List[Dict]:
    """Raspa vagas do Trampos.co"""
    vagas = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://trampos.co/oportunidades", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            cards = await page.query_selector_all(".opportunity-box")
            for card in cards:
                title_el = await card.query_selector("h4")
                title = await title_el.inner_text() if title_el else ""

                link_el = await card.query_selector("a.ember-view.inner")
                link = await link_el.get_attribute("href") if link_el else ""
                if link and not link.startswith("http"):
                    link = f"https://trampos.co{link}"

                company_el = await card.query_selector(".info h5")
                company = await company_el.inner_text() if company_el else ""

                location_el = await card.query_selector(".location")
                location = await location_el.inner_text() if location_el else ""

                type_el = await card.query_selector(".type")
                type_ = await type_el.inner_text() if type_el else ""

                tags_els = await card.query_selector_all(".when .label")
                tags = [await t.inner_text() for t in tags_els]

                if any(kw.lower() in f"{title} {company} {location} {type_} {' '.join(tags)}".lower() for kw in KEYWORDS):
                    vagas.append({
                        "titulo": title.strip(),
                        "url": link,
                        "empresa": company.strip(),
                        "local": location.strip(),
                        "tipo": type_.strip(),
                        "tags": tags,
                        "fonte": "Trampos.co",
                        "data": datetime.now().strftime("%d/%m/%Y")
                    })

            await browser.close()
    except Exception as e:
        logger.error(f"Erro ao raspar Trampos: {e}")
    return vagas


async def fetch_99freelas() -> List[Dict]:
    """Raspa vagas do 99Freelas"""
    vagas = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.99freelas.com.br/projects?category=development", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            cards = await page.query_selector_all("li.result-item")
            for card in cards:
                title_el = await card.query_selector("h1.title a")
                title = await title_el.inner_text() if title_el else ""

                link_el = await card.query_selector("h1.title a")
                link = await link_el.get_attribute("href") if link_el else ""
                if link and not link.startswith("http"):
                    link = f"https://www.99freelas.com.br{link}"

                cat_el = await card.query_selector("p.item-text.information")
                category = await cat_el.inner_text() if cat_el else ""

                desc_el = await card.query_selector("div.item-text.description.formatted-text")
                description = await desc_el.inner_text() if desc_el else ""

                posted_el = await card.query_selector("b.datetime")
                posted = await posted_el.get_attribute("cp-datetime") if posted_el else ""

                prop_els = await card.query_selector_all("p.item-text.information b")
                proposals = [await p.inner_text() for p in prop_els]

                search_text = f"{title} {category} {description}".lower()
                if any(kw.lower() in search_text for kw in KEYWORDS):
                    vagas.append({
                        "titulo": title.strip(),
                        "url": link,
                        "categoria": category.strip(),
                        "descricao": description[:300].strip(),
                        "postado": posted,
                        "propostas": proposals,
                        "fonte": "99Freelas",
                        "data": datetime.now().strftime("%d/%m/%Y")
                    })

            await browser.close()
    except Exception as e:
        logger.error(f"Erro ao raspar 99Freelas: {e}")
    return vagas


async def check_new_vagas() -> List[Dict]:
    global seen_vagas
    all_vagas = []
    all_vagas.extend(await fetch_trampos())
    all_vagas.extend(await fetch_99freelas())

    novas = []
    for vaga in all_vagas:
        identifier = f"{vaga['titulo'][:50]}|{vaga['url']}"
        if identifier not in seen_vagas:
            seen_vagas.add(identifier)
            novas.append(vaga)
    return novas


def format_vaga_message(vaga: Dict) -> str:
    fonte_emoji = "🟢" if vaga["fonte"] == "Trampos.co" else "🔵"
    tags_str = ""
    if "tags" in vaga and vaga["tags"]:
        tags_str = f"\n🏷️ Tags: {', '.join(vaga['tags'])}"
    elif "categoria" in vaga:
        tags_str = f"\n📂 Categoria: {vaga['categoria']}"

    empresa = f"\n🏢 Empresa: {vaga['empresa']}" if "empresa" in vaga and vaga["empresa"] else ""
    local = f"\n📍 Local: {vaga['local']}" if "local" in vaga and vaga["local"] else ""

    return (
        f"{fonte_emoji} <b>NOVA VAGA FREELANCE</b>\n\n"
        f"📋 <b>{vaga['titulo']}</b>{empresa}{local}{tags_str}\n"
        f"🌐 Fonte: {vaga['fonte']}\n"
        f"🔗 Link: {vaga['url']}\n\n"
        f"#Freelance #Vagas #Tech #Python #React #Dev"
    )


async def send_alert(context: ContextTypes.DEFAULT_TYPE, vagas: List[Dict]):
    for vaga in vagas:
        message = format_vaga_message(vaga)
        keyboard = [[InlineKeyboardButton("🔗 Abrir Vaga", url=vaga['url'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            logger.info(f"Alerta enviado: {vaga['titulo'][:50]}")
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")


async def scheduled_check(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Iniciando verificação de vagas...")
    novas = await check_new_vagas()
    if novas:
        logger.info(f"{len(novas)} nova(s) vaga(s) encontrada(s)")
        await send_alert(context, novas)
    else:
        logger.info("Nenhuma vaga nova")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Bot Vagas Freelance ativo!</b>\n\n"
        "Monitoro vagas de desenvolvimento no <b>Trampos.co</b> e <b>99Freelas</b> "
        "e envio alertas automáticos aqui.\n\n"
        "<b>Comandos:</b>\n"
        "/status - Ver status do bot\n"
        "/check - Verificação manual agora\n"
        "/help - Esta mensagem",
        parse_mode="HTML"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ <b>Bot rodando</b>\n"
        f"⏰ Verificação a cada {CHECK_INTERVAL_MINUTES} min\n"
        f"📋 Vagas já vistas: {len(seen_vagas)}\n"
        f"🕐 Última verificação: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        parse_mode="HTML"
    )


async def manual_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Verificando vagas agora...")
    novas = await check_new_vagas()
    if novas:
        await send_alert(context, novas)
        await update.message.reply_text(f"✅ {len(novas)} nova(s) vaga(s) encontrada(s) e alertada(s)!")
    else:
        await update.message.reply_text("📭 Nenhuma vaga nova no momento.")


def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_TOKEN e TELEGRAM_CHAT_ID sao obrigatorios no .env")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("check", manual_check))
    application.add_handler(CommandHandler("help", start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_check,
        trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
        args=[application],
        id="vaga_check",
        replace_existing=True
    )
    scheduler.start()

    logger.info(f"Bot iniciado! Verificando a cada {CHECK_INTERVAL_MINUTES} minutos")

    # Health check HTTP server for Render (port 8080)
    async def health_check(request):
        return web.Response(text="OK", status=200)

    async def start_health_server():
        app = web.Application()
        app.router.add_get("/health", health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        logger.info("Health check server running on port 8080")

    async def run_bot():
        await start_health_server()
        asyncio.get_event_loop().create_task(scheduled_check(application))
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()