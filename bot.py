from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# ================= تنظیمات =================

TOKEN = "8277846112:AAF0nYGl7z2nNhaNqyzsqiG37At4Vwua8Jc"

ADMIN_ID = 24734452

CARD_NUMBER = "5022-2910-5931-2742"


# ================= آموزش ها =================

ANDROID_TUTORIAL = "https://t.me/vpnoneorg/27"

IOS_TUTORIAL = "https://t.me/vpnoneorg/5"

WINDOWS_TUTORIAL = "https://t.me/vpnoneorg/29"



# ================= پلن ها =================

PLANS = {

    "30 گیگ - 3 کاربره - 200/000 تومان": {
        "name": "30 گیگ - 3 کاربره",
        "price": "200/000 تومان"
    },

    "50 گیگ - 3 کاربره - 300/000 تومان": {
        "name": "50 گیگ - 3 کاربره",
        "price": "300/000 تومان"
    },

    "70 گیگ - 3 کاربره - 400/000 تومان": {
        "name": "70 گیگ - 3 کاربره",
        "price": "400/000 تومان"
    },

    "100 گیگ - 3 کاربره - 500/000 تومان": {
        "name": "100 گیگ - 3 کاربره",
        "price": "500/000 تومان"
    },

    "نامحدود - 3 کاربره - 1/000/000 تومان": {
        "name": "نامحدود - 3 کاربره",
        "price": "1/000/000 تومان"
    }

}


orders = {}

send_to_user = None



# ================= منوها =================

def main_menu():

    return ReplyKeyboardMarkup(
        [
            ["💳 خرید VPN"],
            ["📚 آموزش اتصال"],
            ["📞 پشتیبانی"]
        ],
        resize_keyboard=True
    )



def vpn_menu():

    return ReplyKeyboardMarkup(
        [
            ["30 گیگ - 3 کاربره - 200/000 تومان"],
            ["50 گیگ - 3 کاربره - 300/000 تومان"],
            ["70 گیگ - 3 کاربره - 400/000 تومان"],
            ["100 گیگ - 3 کاربره - 500/000 تومان"],
            ["نامحدود - 3 کاربره - 1/000/000 تومان"],
            ["⬅️ بازگشت"]
        ],
        resize_keyboard=True
    )



def tutorial_menu():

    return ReplyKeyboardMarkup(
        [
            ["📱 آموزش اتصال اندروید"],
            ["🍎 آموزش اتصال iOS"],
            ["💻 آموزش اتصال ویندوز"],
            ["⬅️ بازگشت"]
        ],
        resize_keyboard=True
    )



def back_menu():

    return ReplyKeyboardMarkup(
        [
            ["⬅️ بازگشت"]
        ],
        resize_keyboard=True
    )



# ================= شروع =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id


    if user_id == ADMIN_ID:

        await update.message.reply_text(
            "👑 شما ادمین هستید."
        )
        return


    await update.message.reply_text(
        "👋 به VpnOne خوش آمدید",
        reply_markup=main_menu()
    )
    
    # ================= مدیریت پیام ها =================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global send_to_user

    user_id = update.message.from_user.id
    text = update.message.text


    # ================= ادمین =================

    if user_id == ADMIN_ID:

        if send_to_user:

            await context.bot.copy_message(
                chat_id=send_to_user,
                from_chat_id=ADMIN_ID,
                message_id=update.message.message_id
            )

            await update.message.reply_text(
                "✅ برای مشتری ارسال شد."
            )

            send_to_user = None

        return



    # ================= بازگشت =================

    if text == "⬅️ بازگشت":

        await update.message.reply_text(
            "🏠 منوی اصلی:",
            reply_markup=main_menu()
        )

        return



    # ================= آموزش اتصال =================

    if text == "📚 آموزش اتصال":

        await update.message.reply_text(
            "📚 نوع دستگاه را انتخاب کنید:",
            reply_markup=tutorial_menu()
        )

        return



    if text == "📱 آموزش اتصال اندروید":

        await update.message.reply_text(

            f"📱 آموزش اتصال اندروید:\n\n{ANDROID_TUTORIAL}",

            reply_markup=back_menu()

        )

        return



    if text == "🍎 آموزش اتصال iOS":

        await update.message.reply_text(

            f"🍎 آموزش اتصال iOS:\n\n{IOS_TUTORIAL}",

            reply_markup=back_menu()

        )

        return



    if text == "💻 آموزش اتصال ویندوز":

        await update.message.reply_text(

            f"💻 آموزش اتصال ویندوز:\n\n{WINDOWS_TUTORIAL}",

            reply_markup=back_menu()

        )

        return



    # ================= خرید VPN =================

    if text == "💳 خرید VPN":

        await update.message.reply_text(

            "📦 پلن موردنظر را انتخاب کنید:",

            reply_markup=vpn_menu()

        )

        return



    # ================= انتخاب پلن =================

    if text in PLANS:


        orders[user_id] = {

            "plan": PLANS[text]["name"],

            "price": PLANS[text]["price"]

        }


        await update.message.reply_text(

            f"✅ پلن انتخابی:\n"
            f"{orders[user_id]['plan']}\n\n"

            f"💰 مبلغ:\n"
            f"{orders[user_id]['price']}\n\n"

            f"💳 شماره کارت:\n"
            f"{CARD_NUMBER}\n\n"

            "به نام میلاد رحیمی\n\n"

            "📸 لطفاً رسید پرداخت را ارسال کنید."

        )

        return



    # ================= پشتیبانی =================

    if text == "📞 پشتیبانی":

        await update.message.reply_text(

            "📞 پشتیبانی:\n@vpnonesup",

            reply_markup=back_menu()

        )

        return



# ================= دریافت رسید =================

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id


    if user_id == ADMIN_ID:
        return


    if user_id not in orders:

        await update.message.reply_text(
            "❌ ابتدا پلن را انتخاب کنید."
        )

        return



    buttons = [

        [

            InlineKeyboardButton(
                "✅ تایید پرداخت",
                callback_data=f"ok|{user_id}"
            ),

            InlineKeyboardButton(
                "❌ رد پرداخت",
                callback_data=f"no|{user_id}"
            )

        ]

    ]


    await context.bot.send_photo(

        chat_id=ADMIN_ID,

        photo=update.message.photo[-1].file_id,

        caption=

        f"📥 رسید جدید\n\n"
        f"👤 User ID: {user_id}\n"
        f"📦 {orders[user_id]['plan']}\n"
        f"💰 {orders[user_id]['price']}",

        reply_markup=InlineKeyboardMarkup(buttons)

    )


    await update.message.reply_text(

        "✅ رسید شما ارسال شد.\nمنتظر تایید باشید."

    )



# ================= تایید ادمین =================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global send_to_user


    query = update.callback_query

    await query.answer()


    action, user_id = query.data.split("|")

    user_id = int(user_id)



    if action == "ok":


        send_to_user = user_id


        await context.bot.send_message(

            chat_id=user_id,

            text=
            "✅ پرداخت تایید شد.\n"
            "در حال ارسال سرویس..."

        )


        await context.bot.send_message(

            chat_id=ADMIN_ID,

            text=
            "✅ کاربر تایید شد.\n"
            "اکنون لینک، QR، فایل یا کانفیگ را ارسال کنید."

        )



    else:


        await context.bot.send_message(

            chat_id=user_id,

            text="❌ پرداخت شما رد شد."

        )



# ================= اجرای ربات =================


app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CallbackQueryHandler(
        callback_handler
    )
)


app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt_handler
    )
)


app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        message_handler
    )
)


print("VpnOne Bot Running...")


app.run_polling()

