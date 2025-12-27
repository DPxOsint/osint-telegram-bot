from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import requests

BOT_TOKEN = "8579331131:AAEGtDaUK0FeHqup5wA5RR0D2xA6KzAJqYM"

CHANNELS = [
    "@xjthekoaccejnbot",
    "@unlimitedsubscriberbot",
    "@DPxOsintCommunity"
]

# -------- JOIN CHECK --------
async def is_joined(user_id, bot):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


# -------- FORCE JOIN UI --------
def join_keyboard():
    buttons = [
        [InlineKeyboardButton("📢 Join Channel 1", url=f"https://t.me/{CHANNELS[0][1:]}")],
        [InlineKeyboardButton("📢 Join Channel 2", url=f"https://t.me/{CHANNELS[1][1:]}")],
        [InlineKeyboardButton("📢 Join Channel 3", url=f"https://t.me/{CHANNELS[2][1:]}")],
        [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(buttons)


# -------- MAIN MENU --------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Username OSINT", callback_data="username")],
        [InlineKeyboardButton("🌍 IP Lookup", callback_data="ip")],
        [InlineKeyboardButton("🌐 Domain OSINT", callback_data="domain")],
        [InlineKeyboardButton("⚠️ Disclaimer", callback_data="disclaimer")]
    ])


# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_joined(user_id, context.bot):
        await update.message.reply_text(
            "🚫 *Access Restricted*\n\n"
            "Please join all channels to use this bot:",
            reply_markup=join_keyboard()
        )
        return

    await update.message.reply_text(
        "✅ *Welcome to LEGAL OSINT Bot*\n\n"
        "Choose an option below 👇",
        reply_markup=main_menu()
    )


# -------- CALLBACK HANDLER --------
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "check_join":
        if await is_joined(user_id, context.bot):
            await query.edit_message_text(
                "✅ *Access Granted*\n\nSelect OSINT option 👇",
                reply_markup=main_menu()
            )
        else:
            await query.answer("❌ Join all channels first!", show_alert=True)

    elif query.data == "username":
        context.user_data["mode"] = "username"
        await query.edit_message_text("🔍 Send *username* to search:")

    elif query.data == "ip":
        context.user_data["mode"] = "ip"
        await query.edit_message_text("🌍 Send *IP address*:")

    elif query.data == "domain":
        context.user_data["mode"] = "domain"
        await query.edit_message_text("🌐 Send *domain name*:")

    elif query.data == "disclaimer":
        await query.edit_message_text(
            "⚠️ *DISCLAIMER*\n\n"
            "This bot is for educational OSINT purposes only.\n"
            "Uses publicly available data.\n"
            "Illegal usage is strictly prohibited."
        )


# -------- MESSAGE HANDLER --------
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "mode" not in context.user_data:
        return

    text = update.message.text
    mode = context.user_data["mode"]

    if mode == "username":
        await update.message.reply_text(
            f"🔍 *Username OSINT*\n\n"
            f"Instagram: https://instagram.com/{text}\n"
            f"GitHub: https://github.com/{text}\n"
            f"Twitter(X): https://x.com/{text}\n\n"
            "⚠️ Public links only.",
            reply_markup=main_menu()
        )

    elif mode == "ip":
        r = requests.get(f"http://ip-api.com/json/{text}").json()
        if r["status"] != "success":
            await update.message.reply_text("❌ Invalid IP", reply_markup=main_menu())
            return

        await update.message.reply_text(
            f"🌍 *IP Information*\n\n"
            f"IP: {text}\n"
            f"Country: {r['country']}\n"
            f"ISP: {r['isp']}\n"
            f"City: {r['city']}",
            reply_markup=main_menu()
        )

    elif mode == "domain":
        await update.message.reply_text(
            f"🌐 *Domain OSINT*\n\n"
            f"WHOIS: https://who.is/whois/{text}\n"
            f"DNS: https://dnschecker.org/#A/{text}",
            reply_markup=main_menu()
        )

    context.user_data.clear()


# -------- BOT RUN --------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callbacks))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

print("Bot running...")
app.run_polling()