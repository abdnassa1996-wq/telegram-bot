import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "PUT_YOUR_TOKEN_HERE"
ADMIN_ID = 239119174

def load_users(filename):
    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        print(f"⚠️ خطأ في قراءة {filename}، سيتم تهيئة الملف.")
        return set()

def save_users(filename, users_set):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(list(users_set), f, ensure_ascii=False)

approved_users = load_users("approved_users.json")
blocked_users = load_users("blocked_users.json")

WELCOME_TEXT = (
    "مرحبًا بكم،\n"
    "تم إنشاء هذا البوت لدعم وتسهيل العمل المتعلق بمشاريع التحويلات النقدية (الكاش)، "
    "وذلك من خلال استيراد وتنظيم الملفات الورقية والتقنية والبرمجية المعتمدة ضمن المشروع.\n\n"
    "يرجى استخدام القوائم أدناه للوصول إلى الخدمات المتاحة.\n"
    "في حال وجود أي استفسارات أو مقترحات، يمكنكم التواصل مع مشرف البوت."
)

def main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("📁 استيراد ملفات المشاريع", callback_data="menu_projects")],
        [InlineKeyboardButton("🛠️ ملفات مساعدة", callback_data="menu_helpers")],
        [InlineKeyboardButton("📱 تطبيقات", callback_data="menu_apps")],
        [InlineKeyboardButton("🤖 AI", callback_data="menu_ai")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("👤 إدارة المستخدمين", callback_data="manage_users")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    user_id = user.id
    username = user.username or "no_username"

    if user_id in blocked_users:
        if update.message:
            await update.message.reply_text("❌ لا يمكنك استخدام هذا البوت.")
        return

    if user_id not in approved_users:
        keyboard = [[
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
        ]]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"طلب انضمام جديد:\nID: {user_id}\nUsername: @{username}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        if update.message:
            await update.message.reply_text("⏳ تم إرسال طلبك للموافقة من قبل المشرف.")
        return

    is_admin = user_id == ADMIN_ID
    if update.message:
        await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu(is_admin=is_admin))

# باقي دوال buttons كما هي، لا تحتاج تعديل لأنها تعمل مع v20+ وملفات JSON

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(buttons))
        print("Bot is running...")
        app.run_polling()
    except Exception as e:
        print(f"❌ خطأ أثناء تشغيل البوت: {e}")

if __name__ == "__main__":
    main()