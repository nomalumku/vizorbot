import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import google.generativeai as genai

# ============================================
# SOZLAMALAR — shu yerga o'zingiznikini yozing
# ============================================
BOT_TOKEN = "BOTFATHER_DAN_OLGAN_TOKENINGIZ"          # masalan: 7123456789:AAHk3jKL9...
GEMINI_API_KEY = "GEMINI_API_KALITINGIZ"               # masalan: AIzaSyD4f6h8K2...
CHANNEL_USERNAME = "@vizordesign_uz"                    # kanalingiz username'i (boshida @ bilan)
ISM_FAMILIYA = "Ismingiz Familiyangiz"                  # har post tagiga yoziladi

# Premium his beruvchi emoji/stikerlar (matn ko'rinishida, har postga tasodifiy biri qo'shiladi)
STIKERLAR = ["✨", "🎨", "💎", "🔥", "🌟", "👑"]

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
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
