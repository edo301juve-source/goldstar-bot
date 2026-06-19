import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIGURAZIONE =====
BOT_TOKEN = "8965705356:AAELiw-rA3a7XGLqp2fHWiO7su7M7K6rsIQ"
LEAD_GROUP_ID = -5322857475
MINI_APP_URL = "https://edo301juve-source.github.io/goldstar-bot/"

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FLASK APP =====
flask_app = Flask(__name__)

# Loop asyncio condiviso tra Flask e il bot
main_loop = None

@flask_app.route("/", methods=["GET"])
def home():
    return "GoldStar Bot Online ✅", 200

@flask_app.route("/lead", methods=["POST"])
def receive_lead():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400

    maggiorenne = data.get("maggiorenne", "N/D")
    esperienza = data.get("esperienza", "N/D")
    budget = data.get("budget", "N/D")
    servizio = data.get("servizio", "N/D")
    domande = data.get("domande", "—")
    username = data.get("username", "")
    user_id = data.get("user_id", "")

    if username:
        contatto = f"@{username}"
    elif user_id:
        contatto = f"[Scrivi qui](tg://user?id={user_id})"
    else:
        contatto = "Non disponibile"

    messaggio = (
        f"🌟 *NUOVO LEAD GOLDSTAR*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Contatto:* {contatto}\n"
        f"✅ *Maggiorenne:* {maggiorenne}\n"
        f"📊 *Esperienza:* {esperienza}\n"
        f"💰 *Budget:* {budget}\n"
        f"🎯 *Interesse:* {servizio}\n"
        f"💬 *Note:* {domande}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    # Invia il messaggio usando il loop asyncio del bot
    future = asyncio.run_coroutine_threadsafe(
        send_telegram(messaggio), main_loop
    )
    try:
        future.result(timeout=10)
    except Exception as e:
        logger.error(f"Errore invio Telegram: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 200

async def send_telegram(text):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=LEAD_GROUP_ID,
        text=text,
        parse_mode="Markdown"
    )

# ===== COMANDO /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "trader"

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Accedi ai servizi VIP",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Ciao {first_name}!\n\n"
        f"Benvenuto in *GoldStar* ⭐\n\n"
        f"Compila il form per essere contattato dal nostro team e accedere ai servizi VIP.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ===== MAIN =====
async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    # Tieni il bot attivo indefinitamente
    await asyncio.Event().wait()

def start_flask():
    flask_app.run(host="0.0.0.0", port=5000, use_reloader=False)

if __name__ == "__main__":
    # Crea il loop principale
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

    # Avvia Flask in un thread separato
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Avvia il bot nel loop principale
    main_loop.run_until_complete(run_bot())
