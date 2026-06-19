import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== CONFIGURAZIONE =====
BOT_TOKEN = "8965705356:AAELiw-rA3a7XGLqp2fHWiO7su7M7K6rsIQ"
LEAD_GROUP_ID = -5322857475
MINI_APP_URL = "https://TUO_USERNAME.github.io/goldstar-webapp/"  # da aggiornare dopo

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== COMANDO /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "trader"

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Inizia la qualifica",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Ciao {first_name}! Sono *GoldStarEntryBot*.\n\n"
        "Ti guiderò nell'attivazione dei servizi esclusivi. "
        "Rispondi a qualche domanda per trovare quello più adatto a te 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ===== RICEZIONE DATI DALLA MINI APP =====
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = update.message.web_app_data.data

    # Parse dei dati JSON dalla mini app
    import json
    try:
        lead = json.loads(data)
    except:
        lead = {"raw": data}

    # Costruzione messaggio lead
    username = f"@{user.username}" if user.username else f"ID: {user.id}"
    nome = user.first_name or "N/D"
    if user.last_name:
        nome += f" {user.last_name}"

    eta = lead.get("eta", "N/D")
    esperienza = lead.get("esperienza", "N/D")
    budget = lead.get("budget", "N/D")
    servizio = lead.get("servizio", "N/D")
    note = lead.get("note", "") or "—"

    # Se minorenne, non mandare il lead
    if eta == "minorenne":
        await update.message.reply_text(
            "❌ Spiacenti, i nostri servizi sono riservati ai maggiorenni."
        )
        return

    messaggio = (
        f"🆕 *Nuovo lead qualificato*\n\n"
        f"👤 Nome: {nome}\n"
        f"📱 Telegram: {username}\n"
        f"🎯 Esperienza: {esperienza}\n"
        f"💰 Budget: {budget}\n"
        f"📦 Servizio: {servizio}\n"
        f"📝 Note: {note}"
    )

    # Manda al gruppo lead
    await context.bot.send_message(
        chat_id=LEAD_GROUP_ID,
        text=messaggio,
        parse_mode="Markdown"
    )

    # Conferma all'utente
    await update.message.reply_text(
        "✅ Perfetto! Il nostro team ti contatterà a breve su Telegram.\n\n"
        "Nel frattempo puoi seguire il canale per restare aggiornato. ⭐"
    )

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    logger.info("Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
