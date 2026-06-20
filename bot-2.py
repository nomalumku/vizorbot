import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import google.generativeai as genai

# ============================================
# SOZLAMALAR — shu yerga o'zingiznikini yozing
# ============================================
BOT_TOKEN = "8874863992:AAH0HZ5cNqFnzW9qsRvW-zNxFXkXwCjfI40"
GEMINI_API_KEY = "AIAQ.Ab8RN6IZFamRrn_NHYr35Y-pftMxpfWkXao_LNhueh5hHeK3nA"
CHANNEL_USERNAME = "@vizor_design"
ISM_FAMILIYA = "Xojiakbar Jo'rayev"

# Premium his beruvchi emoji/stikerlar (matn ko'rinishida, har postga tasodifiy biri qo'shiladi)
STIKERLAR = ["✨", "🎨", "💎", "🔥", "🌟", "👑"]

# ============================================
# Veb-server qismi — Render bepul tarifi uchun kerak
# (Bu botni "veb-xizmat" deb ko'rsatadi, lekin asl ishi o'zgarmaydi)
# ============================================

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot ishlab turibdi.")

    def log_message(self, format, *args):
        pass  # ortiqcha loglarni o'chirish


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()


# ============================================
# Tizim qismi — bu joyni o'zgartirish shart emas
# ============================================

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

import random


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi botga rasm yuborganda ishga tushadi."""
    try:
        await update.message.reply_text("Qabul qildim, izoh yozyapman... ⏳")

        # Eng katta sifatdagi rasmni olish
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Gemini'ga rasmni yuborib, izoh so'rash
        caption = generate_caption(bytes(photo_bytes))

        # Stiker va ism-familiya qo'shish
        stiker = random.choice(STIKERLAR)
        final_caption = f"{caption}\n\n{stiker} {ISM_FAMILIYA}"

        # Kanalga rasmni izoh bilan birga joylash
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=bytes(photo_bytes),
            caption=final_caption,
        )

        await update.message.reply_text("Kanalga muvaffaqiyatli joylandi ✅")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")


def generate_caption(image_bytes: bytes) -> str:
    """Gemini AI orqali rasmga mos izoh yaratish."""
    prompt = (
        "Bu grafik dizayn ishi. O'zbek tilida, Telegram kanal posti uchun "
        "qisqa, professional va jozibali izoh yoz (2-3 gap). "
        "Dizayn uslubi, ranglar yoki kompozitsiya haqida gapir. "
        "Oxirida 2-3 ta mos hashtag qo'sh (#dizayn #grafikdizayn kabi)."
    )
    response = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
    )
    return response.text.strip()


def main():
    # Veb-server alohida thread'da ishga tushadi (Render bepul tarifi shuni talab qiladi)
    threading.Thread(target=run_web_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True, close_loop=False)


if __name__ == "__main__":
    main()
