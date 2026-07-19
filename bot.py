from database import (
    init_db,
    add_user,
    add_order,
    get_users,
    get_user,
    get_orders,
    get_pending_orders,
    get_sales_count,
    update_order_status,
    get_user_orders,
    get_user_active_orders,
    get_user_active_service,
    delete_user,
)

from database import save_user_service

import os

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
from telegram import KeyboardButton

# ================= تنظیمات =================

TOKEN = os.getenv("BOT_TOKEN")

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
send_message_mode = None
config_mode = None

# ================= منوها =================

def main_menu():

    return ReplyKeyboardMarkup(
        [
            ["💳 خرید VPN"],
            ["📡 سرویس من"],
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


def admin_menu():

    return ReplyKeyboardMarkup(
        [
            ["👥 کاربران"],
            ["📦 سفارش‌ها"],
            ["⏳ سفارش‌های در انتظار"],
            ["📊 آمار فروش"],
            ["📨 ارسال پیام"],
            ["📡 ثبت اشتراک"],
            ["🗑 حذف کاربر"],
        ],
        resize_keyboard=True
    )
# ================= شروع =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    await add_user(
        user.id,
        user.username,
        user.first_name
    )

    user_id = user.id


    if user_id == ADMIN_ID:

        await update.message.reply_text(
            "👑 پنل مدیریت VpnOne",
            reply_markup=admin_menu()
        )

        return


    await update.message.reply_text(
        "👋 به VpnOne خوش آمدید",
        reply_markup=main_menu()
    )
# ================= مدیریت پیام ها =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        return


    await update.message.reply_text(
        "👑 پنل مدیریت VpnOne",
        reply_markup=admin_menu()
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global send_to_user
    global send_message_mode
    global config_mode

    user_id = update.message.from_user.id
    text = update.message.text
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name


    await add_user(
        user_id,
        username,
        first_name
    )


# ================= ادمین =================

    if user_id == ADMIN_ID:


        if text == "👥 کاربران":

            users = await get_users()

            if not users:
                await update.message.reply_text(
                    "❌ هنوز کاربری ثبت نشده."
                )
                return


            msg = "👥 کاربران:\n\n"


            for user in users[:20]:
                if user[0] == ADMIN_ID:
                    continue

                service = await get_user_active_service(user[0])

                if service:
                    plan = service[0]
                    price = service[1]
                    config = service[2]
                    expire_date = service[3]
                else:
                    plan = "نامشخص"
                    price = "نامشخص"
                    config = "نامشخص"
                    expire_date = "نامشخص"


                msg += (
                    f"🆔 {user[0]}\n"
                    f"👤 {user[1] or 'بدون یوزرنیم'}\n"
                    f"👨 {user[2]}\n"
                    f"📦 اشتراک: {plan}\n"
                    f"📡 لینک اشتراک:\n{config}\n"
                    f"📅 انقضا: {expire}\n\n"
                    "━━━━━━━━━━━━\n\n"
                )


            await update.message.reply_text(msg)

            return



        if text == "📦 سفارش‌ها":

            orders_list = await get_orders()

            if not orders_list:

                await update.message.reply_text(
                    "❌ سفارشی وجود ندارد."
                )

                return


            msg = "📦 سفارش‌ها:\n\n"


            for order in orders_list[:20]:

                msg += (
                    f"شماره: {order[0]}\n"
                    f"کاربر: {order[1]}\n"
                    f"پلن: {order[2]}\n"
                    f"مبلغ: {order[3]}\n"
                    f"وضعیت: {order[4]}\n\n"
                )


            await update.message.reply_text(msg)

            return



        if text == "⏳ سفارش‌های در انتظار":

            pending = await get_pending_orders()


            if not pending:

                await update.message.reply_text(
                    "✅ سفارش در انتظاری نیست."
                )

                return


            msg = "⏳ سفارش‌های در انتظار:\n\n"


            for order in pending:

                msg += (
                    f"🆔 سفارش: {order[0]}\n"
                    f"کاربر: {order[1]}\n"
                    f"پلن: {order[2]}\n"
                    f"مبلغ: {order[3]}\n\n"
                )


            await update.message.reply_text(msg)

            return



        if text == "📊 آمار فروش":

            count = await get_sales_count()

            await update.message.reply_text(
                f"📊 تعداد فروش موفق: {count}"
            )

            return



        if text == "📨 ارسال پیام":

            send_message_mode = "get_id"
            config_mode = None

            await update.message.reply_text(
                "🆔 آیدی عددی کاربر را ارسال کنید:"
            )

            return

    # دریافت آیدی کاربر برای ارسال پیام

        if send_message_mode == "get_id":

            try:

                send_to_user = int(text)

                send_message_mode = "send_text"


                await update.message.reply_text(
                    "✏️ متن پیام را ارسال کنید:"
                )


            except:

                await update.message.reply_text(
                    "❌ آیدی باید عدد باشد."
                )


            return

        # ارسال متن پیام به کاربر

        if send_message_mode == "send_text":

            await context.bot.send_message(
                chat_id=send_to_user,
                text=text
            )

            await update.message.reply_text(
                "✅ پیام ارسال شد."
            )

            send_message_mode = None
            send_to_user = None

            return



        # ارسال پیام به کاربر

        if text == "📡 ثبت اشتراک":

            config_mode = "get_id"
            send_message_mode = None

            await update.message.reply_text(
                "🆔 آیدی کاربر را ارسال کنید:"
            )

            return


        # دریافت آیدی برای ثبت اشتراک

        if config_mode == "get_id":

            try:

                send_to_user = int(text)

                config_mode = "get_config"


                await update.message.reply_text(
                    "🔗 لینک اشتراک را ارسال کنید:"
                )


            except:

                await update.message.reply_text(
                    "❌ آیدی اشتباه است."
                )

            return



        # دریافت لینک اشتراک

        if config_mode == "get_config":

            await save_user_service(
                send_to_user,
                text,
                username,
                first_name
            )
            
            service = await get_user_active_service(send_to_user)

            if service:
                expire_date = service[1]
            else:
                expire_date = "نامشخص"
                
            get_user_info = await get_user(send_to_user)


            await context.bot.send_message(
                chat_id=send_to_user,
                text=
                "✅ سرویس شما فعال شد.\n\n"
                f"📦 پلن: {service[0]}\n"
                f"💰 مبلغ: {price} تومان\n\n"
                "🔗 لینک اشتراک:\n"
                f"{text}\n\n"
                f"📅 تاریخ انقضا: {expire_date}\n\n"
                "✅ وضعیت: فعال"
            )
            
            
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=
                "✅ اشتراک جدید ثبت شد\n\n"
                f"🆔 {send_to_user}\n"
                f"👤 {get_user_info[0] or 'بدون یوزرنیم'}\n"
                f"👨 {get_user_info[1]}\n"
                f"📡 لینک اشتراک:\n{text}\n"
                f"📅 انقضا: {expire_date}"
            )


            config_mode = None
            send_to_user = None

            return
        
        if config_mode == "delete_user":

            delete_id = int(text)

            await delete_user(delete_id)

            await update.message.reply_text(
                "✅ کاربر حذف شد."
            )

            config_mode = None

            return
        
        
        if text == "🗑 حذف کاربر":

            config_mode = "delete_user"

            await update.message.reply_text(
                "🆔 آیدی کاربری که می‌خواهید حذف کنید را ارسال کنید:"
            )

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


    # ================= سرویس من =================

    if text == "📡 سرویس من":

        services = await get_user_active_orders(user_id)

        if not services:

            await update.message.reply_text(
                "❌ هنوز سرویس فعالی ندارید.",
                reply_markup=main_menu()
            )

            return


        msg = "📡 سرویس‌های فعال شما:\n\n"


        for service in services:

            msg += (
                f"📦 پلن: {service[0]}\n"
                f"💰 مبلغ: {service[1]}\n\n"
                f"🔗 لینک اشتراک:\n"
                f"{service[2] if service[2] else 'ثبت نشده'}\n\n"
                f"📅 تاریخ انقضا: "
                f"{service[3] if service[3] else 'ثبت نشده'}\n\n"
                f"✅ وضعیت: فعال\n\n"
            )


        await update.message.reply_text(
            msg,
            reply_markup=main_menu()
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
        
        await add_order(
            user_id,
            PLANS[text]["name"],
            PLANS[text]["price"]
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
    global send_message_mode
    global config_mode

    query = update.callback_query

    await query.answer()
   
    print("BUTTON CLICKED:", query.data)
 
    action, user_id = query.data.split("|")

    user_id = int(user_id)


    if action == "ok":

        send_to_user = user_id


        await update_order_status(
            user_id,
            "approved"
        )


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


    elif action == "no":

        await update_order_status(
            user_id,
            "rejected"
        )


        await context.bot.send_message(
            chat_id=user_id,
            text="❌ پرداخت شما رد شد."
        )



# ================= اجرای ربات =================

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set!"
    )


app = Application.builder().token(TOKEN).build()


# start اول باشد
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CommandHandler(
        "admin",
        admin
    )
)


app.add_handler(
    CallbackQueryHandler(
        callback_handler
    )
)


# عکس رسید
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt_handler
    )
)


# پیام‌های معمولی آخر باشد
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    )
)

print("VpnOne Bot Running...")


import asyncio


async def main():

    await init_db()

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()


asyncio.run(main())