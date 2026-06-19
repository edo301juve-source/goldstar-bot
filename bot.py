import logging
import os
import threading
import asyncio
from flask import Flask, request, jsonify
import httpx

# ===== CONFIGURAZIONE =====
BOT_TOKEN = "8965705356:AAELiw-rA3a7XGLqp2fHWiO7su7M7K6rsIQ"
LEAD_GROUP_ID = -5322857475
MINI_APP_URL = "https://edo301juve-source.github.io/goldstar-bot/"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FLASK =====
flask_app = Flask(__name__)

def send_telegram_sync(text):
    """Invia messaggio Telegram in modo sincrono tramite httpx"""
    try:
        r = httpx.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": LEAD_GROUP_ID,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        logger.info(f"Telegram response: {r.status_code} {r.text}")
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Errore invio Telegram: {e}")
        return False

@flask_app.route("/", methods=["GET"])
def home():
    return "GoldStar Bot Online ✅", 200

@flask_app.route("/lead", methods=["POST"])
def receive_lead():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400

    maggiorenne = data.get("maggiorenne", "N/D")
    esperienza  = data.get("esperienza", "N/D")
    budget      = data.get("budget", "N/D")
    servizio    = data.get("servizio", "N/D")
    domande     = data.get("domande", "—")
    username    = data.get("username", "")
    user_id     = data.get("user_id", "")

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

    ok = send_telegram_sync(messaggio)
    if ok:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"error": "Telegram send failed"}), 500

# ===== BOT POLLING (thread separato) =====
def run_polling():
    """Polling semplice con httpx - nessuna dipendenza da python-telegram-bot"""
    offset = None
    logger.info("Bot polling avviato")
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            r = httpx.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=35)
            updates = r.json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                first_name = msg.get("from", {}).get("first_name", "trader")
                if text == "/start" and chat_id:
                    send_start(chat_id, first_name)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            import time; time.sleep(5)

def send_start(chat_id, first_name):
    """Manda il messaggio /start con bottone mini app"""
    payload = {
        "chat_id": chat_id,
        "text": (
            f"👋 Ciao {first_name}\\!\n\n"
            f"Benvenuto in *GoldStar* ⭐\n\n"
            f"Compila il form per essere contattato dal nostro team e accedere ai servizi VIP\\."
        ),
        "parse_mode": "MarkdownV2",
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "🚀 Accedi ai servizi VIP",
                    "web_app": {"url": MINI_APP_URL}
                }
            ]]
        }
    }
    try:
        httpx.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Errore send_start: {e}")

if __name__ == "__main__":
    # Avvia il polling in background
    t = threading.Thread(target=run_polling, daemon=True)
    t.start()
    # Avvia Flask
    flask_app.run(host="0.0.0.0", port=5000, use_reloader=False)
