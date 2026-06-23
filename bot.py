
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8789214955:AAEbd-g_V-8fgKYLe84BbC4mqWODCB0JM4A"
ADMIN_ID = 6430735687

users = {}
pairs = {}
waiting = {"any": []}

main_menu = ReplyKeyboardMarkup([
    ["💬 شروع چت", "👤 پروفایل"],
    ["🔁 Next", "⛔ قطع چت"]
], resize_keyboard=True)


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

    for partner in list(pool):
        if partner != user_id:
            pool.remove(partner)

            pairs[user_id] = partner
            pairs[partner] = user_id

            await context.bot.send_message(user_id, "✅ وصل شدی", reply_markup=main_menu)
            await context.bot.send_message(partner, "✅ یک نفر وصل شد", reply_markup=main_menu)
            return

    if user_id not in pool:
        pool.append(user_id)
        await context.bot.send_message(user_id, "⏳ در حال پیدا کردن کاربر...")


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
        if user_id in pairs:
            partner = pairs.pop(user_id)
            pairs.pop(partner, None)

            waiting["any"].extend([user_id, partner])

            await context.bot.send_message(partner, "🔁 کاربر رفت")
            await context.bot.send_message(user_id, "🔁 در حال اتصال جدید...")

            await connect(user_id, context)
            await connect(partner, context)
        return

    if text == "⛔ قطع چت":
        if user_id in pairs:
            partner = pairs.pop(user_id)
            pairs.pop(partner, None)

            waiting["any"].extend([user_id, partner])

            await context.bot.send_message(partner, "⛔ چت قطع شد")
            await update.message.reply_text("⛔ چت قطع شد")
        else:
            await update.message.reply_text("❌ در چت نیستی")
        return

    if user_id in pairs:
        partner = pairs[user_id]
        await context.bot.send_message(partner, text)
    else:
        await update.message.reply_text("❌ هنوز وصل نیستی")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    app.run_polling()


if __name__ == "__main__":
    main()
