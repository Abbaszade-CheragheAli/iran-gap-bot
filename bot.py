from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ================== CONFIG (اینجا رو تغییر بده) ==================
BOT_TOKEN = "8789214955:AAELycg1_gFw9k8jh9W0talc6rMJSCkffZo"
ADMIN_ID = 6430735687   # آیدی عددی خودت
# ================================================================

users = {}
pairs = {}
waiting = {"any": []}

main_menu = ReplyKeyboardMarkup([
    ["💬 شروع چت", "👤 پروفایل"],
    ["🔁 Next", "⛔ قطع چت"]
], resize_keyboard=True)

chat_menu = main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 خوش اومدی به ایران گپ", reply_markup=main_menu)


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = users.get(user_id, {})

    text = f"""
👤 پروفایل:

🧑 اسم: {u.get('name','ثبت نشده')}
🎂 سن: {u.get('age','ثبت نشده')}
🚻 جنسیت: {u.get('gender','ثبت نشده')}
"""

    await update.message.reply_text(text)


async def connect(user_id, context):
    pool = waiting["any"]

    for partner in pool:
        if partner != user_id:
            pool.remove(partner)

            pairs[user_id] = partner
            pairs[partner] = user_id

            await context.bot.send_message(user_id, "✅ وصل شدی", reply_markup=chat_menu)
            await context.bot.send_message(partner, "✅ یک نفر وصل شد", reply_markup=chat_menu)
            return

    if user_id not in pool:
        pool.append(user_id)
        await context.bot.send_message(user_id, "⏳ در حال پیدا کردن کاربر...")


async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await connect(update.effective_user.id, context)


async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in pairs:
        partner = pairs[user_id]

        del pairs[user_id]
        del pairs[partner]

        waiting["any"].append(user_id)
        waiting["any"].append(partner)

        await context.bot.send_message(partner, "🔁 کاربر رفت")
        await context.bot.send_message(user_id, "🔁 در حال اتصال جدید...")

        await connect(user_id, context)
        await connect(partner, context)


async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in pairs:
        await update.message.reply_text("❌ در چت نیستی")
        return

    partner = pairs[user_id]

    del pairs[user_id]
    del pairs[partner]

    waiting["any"].append(user_id)
    waiting["any"].append(partner)

    await context.bot.send_message(partner, "⛔ چت قطع شد")
    await update.message.reply_text("⛔ چت قطع شد")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "💬 شروع چت":
        await connect(user_id, context)
        return

    if text == "👤 پروفایل":
        await profile(update, context)
        return

    if text == "🔁 Next":
        await next_chat(update, context)
        return

    if text == "⛔ قطع چت":
        await end_chat(update, context)
        return

    if user_id in pairs:
        partner = pairs[user_id]
        await context.bot.send_message(partner, text)
    else:
        await update.message.reply_text("❌ هنوز وصل نیستی")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
