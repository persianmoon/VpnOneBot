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
    delete_users,
    delete_order,
    delete_all_orders,
    renew_order
)

from database import save_user_service

import os

from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDate

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

CARD_NUMBER = "`5022-2910-5931-2742`"


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
selected_plan = None
selected_price = None
selected_config = None
broadcast_mode = None
user_message_mode = None
user_renew_mode = None
renew_mode = None
selected_renew_order = None
renew_selected_service = None
renew_request = None
renew_users = {}

users_page = 0
orders_page = 0

# ================= منوها =================

def main_menu():

    return ReplyKeyboardMarkup(
        [
            ["💳 خرید VPN","📡 سرویس من"],
            ["🔄 تمدید اشتراک","📨 ارسال پیام به پشتیبانی"],
            ["📚 آموزش اتصال","📞 پشتیبانی"]
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
            ["📱 آموزش اتصال اندروید","🍎 آموزش اتصال iOS"],
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
            ["👥 کاربران","📦 سفارش‌ها"],
            ["⏳ سفارش‌های در انتظار","📊 آمار فروش"],
            ["📨 ارسال پیام","📢 ارسال همگانی"],
            ["🗑 حذف کاربر","📡 ثبت اشتراک"],
        ],
        resize_keyboard=True
    )

def plan_menu():

    return ReplyKeyboardMarkup(
        [
            ["30 گیگ - 3 کاربره - 200/000 تومان"],
            ["50 گیگ - 3 کاربره - 300/000 تومان"],
            ["70 گیگ - 3 کاربره - 400/000 تومان"],
            ["100 گیگ - 3 کاربره - 500/000 تومان"],
            ["نامحدود - 3 کاربره - 1/000/000 تومان"],
        ],
        resize_keyboard=True
    )


def renew_plan_menu():

    return ReplyKeyboardMarkup(
        [
            ["30 گیگ - 3 کاربره - 200/000 تومان"],
            ["50 گیگ - 3 کاربره - 300/000 تومان"],
            ["70 گیگ - 3 کاربره - 400/000 تومان"],
            ["100 گیگ - 3 کاربره - 500/000 تومان"],
            ["نامحدود - 3 کاربره - 1/000/000 تومان"],
            ["⬅️ بازگشت به منوی اصلی"]
        ],
        resize_keyboard=True
    )



def orders_menu():

    return ReplyKeyboardMarkup(
        [
            ["🗑 حذف سفارش", "🔥 حذف همه سفارش‌ها"],
            ["⬅️ برگشت به مدیریت"]
        ],
        resize_keyboard=True
    )


def renew_service_menu(services):

    buttons = []

    for index, service in enumerate(services):

        buttons.append(
            [
                f"{service[0]} - {service[1]}"
            ]
        )


    buttons.append(
        ["⬅️ بازگشت"]
    )


    return ReplyKeyboardMarkup(
        buttons,
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

    global config_mode
    global send_to_user
    global send_message_mode
    global selected_plan
    global selected_price
    global selected_config
    global users_page
    global orders_page
    global broadcast_mode
    global renew_mode
    global renew_selected_service
    global renew_request

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


        if text == "⬅️ برگشت به مدیریت":

            await update.message.reply_text(
                "⚙️ پنل مدیریت",
                reply_markup=admin_menu()
            )

            users_page = 0
            orders_page = 0

            return
        
        if text == "بعدی ➡️":

            users_page += 1

            users = await get_users()

            page_size = 10

            if users_page * page_size >= len(users):

                users_page -= 1

                await update.message.reply_text(
                    "❌ صفحه دیگری وجود ندارد."
                )

                return
            
            text = "👥 کاربران"
            
            
        if text == "⬅️ قبلی":

            if users_page > 0:

                users_page -= 1

            else:

                await update.message.reply_text(
                    "❌ این اولین صفحه است."
                )

                return
        

            text = "👥 کاربران"
    
        
        if text == "👥 کاربران":

            users = await get_users()

            if not users:
                await update.message.reply_text(
                    "❌ هنوز کاربری ثبت نشده."
                )
                return
            
            page_size = 10

            start = users_page * page_size

            end = start + page_size

            page_users = users[start:end]


            msg = f"👥 کاربران (صفحه {users_page + 1}):\n\n"


            for user in page_users:
                if user[0] == ADMIN_ID:
                    continue

                services = await get_user_active_orders(user[0])

                if services:

                    service_text = ""

                    for s in services:

                        service_text += (
                            f"📦 پلن: {s[0]}\n"
                            f"💰 مبلغ: {s[1]}\n"
                            f"📡 لینک اشتراک:\n{s[2]}\n"
                            f"📅 انقضا: {s[3]}\n\n"
                            "━━━━━━━━━━━━\n"
                    )

                else:

                    service_text = "❌ ندارد"


                msg += (
                    f"🆔 {user[0]}\n"
                    f"👤 {user[1] or 'بدون یوزرنیم'}\n"
                    f"👨 {user[2]}\n\n"
                    f"📦 اشتراک‌ها:\n{service_text}\n"
                    "━━━━━━━━━━━━\n\n"
                )


            await update.message.reply_text(
                msg,
                reply_markup=users_pagination_menu()
            )

            return



        # ================= حذف سفارش =================

        if text == "🗑 حذف سفارش":

            config_mode = "delete_order"

            await update.message.reply_text(
                "🆔 آیدی سفارش را ارسال کنید:"
            )

            return


        if config_mode == "delete_order":
            
            print("DELETE ORDER MODE:", text)

            try:
                order_id = int(text)
    
                await delete_order(order_id)

                await update.message.reply_text(
                    "✅ سفارش حذف شد."
                )

            except:

                await update.message.reply_text(
                    "❌ آیدی سفارش اشتباه است."
                )

            config_mode = None

            return


        if text == "🔥 حذف همه سفارش‌ها":

            try:

                await delete_all_orders()

                await update.message.reply_text(
                    "✅ تمام سفارش‌ها حذف شدند."
                )

            except Exception as e:

                await update.message.reply_text(
                    f"❌ خطا:\n{e}"
                )

            return



        # ================= نمایش سفارش‌ها =================

        if text == "📦 سفارش‌ها":

            orders_list = await get_orders()

            if not orders_list:

                await update.message.reply_text(
                    "❌ سفارشی وجود ندارد.",
                    reply_markup=orders_menu()
                )

                return


            msg = "📦 سفارش‌ها:\n\n"


            for order in orders_list[:20]:

                user_info = await get_user(order[1])

                msg += (
                    f"🆔 سفارش: {order[0]}\n"
                    f"👤 آیدی کاربر: {order[1]}\n"
                    f"📛 یوزرنیم: @{user_info[0] or 'ندارد'}\n"
                    f"👨 نام: {user_info[1] or 'ندارد'}\n"
                    f"📦 پلن: {order[2]}\n"
                    f"💰 مبلغ: {order[3]}\n"
                    f"📌 وضعیت: {order[4]}\n\n"
                    "━━━━━━━━━━━━\n\n"
                )


            await update.message.reply_text(
                msg,
                reply_markup=orders_menu()
            )

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


        if text == "📢 ارسال همگانی":

            broadcast_mode = "send"

            await update.message.reply_text(
                "📢 متن پیام همگانی را ارسال کنید:"
            )

            return
        
        
        
        if broadcast_mode == "send":

            users = await get_users()

            success = 0
            failed = 0

            for user in users:

                try:

                    if user[0] == ADMIN_ID:
                        continue

                    await context.bot.send_message(
                        chat_id=user[0],
                        text=text
                    )

                    success += 1

                except:

                    failed += 1


            await update.message.reply_text(
                f"✅ ارسال همگانی انجام شد.\n\n"
                f"📨 موفق: {success}\n"
                f"❌ ناموفق: {failed}",
                reply_markup=admin_menu()
            )


            broadcast_mode = None

            return
        
        

        if text == "📡 ثبت اشتراک":

            config_mode = "get_id"
            send_message_mode = None

            print("CONFIG MODE SET:", config_mode)

            await update.message.reply_text(
                "🆔 آیدی کاربر را ارسال کنید:"
            )

            return


        # دریافت آیدی برای ثبت اشتراک

        if config_mode == "get_id":
            
            print("GET ID RUNNING:", text)


            try:

                send_to_user = int(text)

                config_mode = "select_plan"

                await update.message.reply_text(
                    "📦 پلن را انتخاب کنید:",
                    reply_markup=plan_menu()
                )


            except Exception as e:

                print(e)

                await update.message.reply_text(
                   f"❌ خطا:\n{e}"
                )

            return

        if config_mode == "select_plan":

            if text not in PLANS:

                await update.message.reply_text(
                    "❌ لطفاً یکی از پلن‌ها را انتخاب کنید.",
                    reply_markup=plan_menu()
                )

                return

            selected_plan = PLANS[text]["name"]
            selected_price = PLANS[text]["price"]

            config_mode = "get_config"

            await update.message.reply_text(
                "🔗 لینک اشتراک را ارسال کنید:"
            )
    
            return


        # دریافت لینک اشتراک

        if config_mode == "get_config":

            selected_config = text

            config_mode = "get_buy_date"

            await update.message.reply_text(
                "📅 تاریخ خرید را وارد کنید:\n\nمثال:\n1405/04/30"
            )

            return
        
        
        if config_mode == "get_buy_date":

            try:

                buy_date = JalaliDate.strptime(
                    text,
                    "%Y/%m/%d"
                )

                expire_date = (
                    JalaliDate(
                        buy_date.to_gregorian() + timedelta(days=30)
                    )
                    .strftime("%Y/%m/%d")
                )


                await save_user_service(
                    send_to_user,
                    selected_config,
                    username,
                    first_name,
                    selected_plan,
                    selected_price,
                    buy_date.strftime("%Y/%m/%d"),
                    expire_date
                )


                await update.message.reply_text(
                    "✅ اشتراک ثبت شد.\n\n"
                    f"📅 تاریخ خرید: {buy_date.strftime('%Y/%m/%d')}\n"
                    f"📅 تاریخ انقضا: {expire_date}",
                    reply_markup=admin_menu()
                )


                config_mode = None
                send_to_user = None

            except Exception as e:

                await update.message.reply_text(
                    f"❌ فرمت تاریخ اشتباه است.\n{e}"
                )

            return


            
                
            get_user_info = await get_user(send_to_user)


            await context.bot.send_message(
                chat_id=send_to_user,
                text=
                "✅ سرویس شما فعال شد.\n\n"
                f"📦 پلن: {selected_plan}\n"
                f"💰 مبلغ: {selected_price}\n\n"
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
        
        if text == "🗑 حذف کاربر":

            config_mode = "delete_user"

            await update.message.reply_text(
                "🆔 آیدی کاربری که می‌خواهید حذف کنید را ارسال کنید:"
            )

            return


        if config_mode == "delete_user":

            try:

                lines = text.splitlines()

                user_ids = []

                for line in lines:
                    user_ids.append(int(line.strip()))


                await delete_users(user_ids)


                await update.message.reply_text(
                    f"✅ تعداد {len(user_ids)} کاربر حذف شد."
                )


            except Exception as e:

                await update.message.reply_text(
                    f"❌ خطا:\n{e}"
                )


            config_mode = None

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


    # ================= تمدید اشتراک =================

    if text == "🔄 تمدید اشتراک":
        
        services = await get_user_active_orders(user_id)

        if not services:

            await update.message.reply_text(
                "❌ شما سرویس فعالی ندارید.",
                reply_markup=main_menu()
            )

            return


        renew_mode = "select_service"

        await update.message.reply_text(
            "🔄 سرویس موردنظر برای تمدید را انتخاب کنید:",
            reply_markup=renew_service_menu(services)
        )

    
    
    if renew_mode == "select_service":

        services = await get_user_active_orders(user_id)

        for service in services:

            button_text = f"{service[0]} - {service[1]}"

            if text == button_text:

                renew_selected_service = service

                renew_mode = "select_plan"
    

                await update.message.reply_text(
                    "📦 پلن جدید برای تمدید را انتخاب کنید:",
                     reply_markup=renew_plan_menu()
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

            expire_date = service[3]

            if expire_date:

                try:
                    # تاریخ شمسی قدیمی
                    expire = JalaliDate.strptime(
                        expire_date,
                        "%Y/%m/%d"
                    )

                except:

                    # تاریخ میلادی جدید
                    from datetime import datetime

                    gregorian_date = datetime.strptime(
                        expire_date,
                        "%Y-%m-%d"
                    ).date()

                    expire = JalaliDate.to_jalali(
                        gregorian_date
                    )


                today = JalaliDate.today()

                days_left = (expire - today).days

                if days_left < 0:
                    days_left = 0

            else:
                days_left = "نامشخص"


            msg += (
                f"📦 پلن: {service[0]}\n"
                f"💰 مبلغ: {service[1]}\n\n"
                f"🔗 لینک اشتراک:\n"
                f"{service[2] if service[2] else 'ثبت نشده'}\n\n"
                f"📅 تاریخ انقضا: {expire_date if expire_date else 'ثبت نشده'}\n"
                f"⏳ روزهای باقی‌مانده: {days_left} روز\n\n"
                f"✅ وضعیت: فعال\n\n"
                "━━━━━━━━━━━━━━\n\n"
            )


        await update.message.reply_text(
            msg,
            reply_markup=main_menu()
        )

        return
    
    if text == "📨 ارسال پیام به پشتیبانی":

        send_message_mode = "support"

        await update.message.reply_text(
            "✏️ پیام خود را ارسال کنید:",
            reply_markup=back_menu()
        )

        return
    
    
    if send_message_mode == "support":

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=
            f"📨 پیام جدید از کاربر\n\n"
            f"🆔 آیدی: {user_id}\n"
            f"👤 یوزرنیم: @{username or 'ندارد'}\n"
            f"👨 نام: {first_name or 'ندارد'}\n\n"
            f"💬 پیام:\n{text}"
        )


        await update.message.reply_text(
            "✅ پیام شما برای پشتیبانی ارسال شد.",
            reply_markup=main_menu()
        )


        send_message_mode = None

        return


    # ================= خرید VPN =================

    if text == "💳 خرید VPN":

        await update.message.reply_text(
            "📦 پلن موردنظر را انتخاب کنید:",
            reply_markup=vpn_menu()
        )

        return



    # ================= بازگشت کلی =================

    if text == "⬅️ بازگشت به منوی اصلی":

        renew_mode = None

        if user_id in renew_users:
            del renew_users[user_id]

        await update.message.reply_text(
            "🏠 منوی اصلی:",
            reply_markup=main_menu()
        )

        return



    # ================= تمدید اشتراک =================

    if renew_mode == "select_plan":
        
        
        print("RENEW SELECT PLAN RUNNING:", text)
        print("RENEW MODE:", renew_mode)

        if text not in PLANS:
            await update.message.reply_text(
                "❌ لطفاً یکی از پلن‌ها را انتخاب کنید.",
                reply_markup=renew_plan_menu()
            )
            return


        renew_request = {
            "user_id": user_id,
            "old_service": renew_selected_service,
            "new_plan": PLANS[text]["name"],
            "new_price": PLANS[text]["price"]
        }
        
        
        renew_users[user_id] = {
            "plan": PLANS[text]["name"],
            "price": PLANS[text]["price"],
            "old_service": renew_selected_service
        }
        
        print("RENEW SAVED:", renew_users)


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

            "📸 لطفاً رسید پرداخت را ارسال کنید.",

            parse_mode="Markdown"
        )

        renew_mode = None
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

            "📸 لطفاً رسید پرداخت را ارسال کنید.",
            
            parse_mode="Markdown"

        )
        
        await add_order(
            user_id,
            PLANS[text]["name"],
            PLANS[text]["price"],
        )



    # ================= پشتیبانی =================

    if text == "📞 پشتیبانی":

        await update.message.reply_text(

            "📞 پشتیبانی:\n@vpnonesup",

            reply_markup=back_menu()

        )

        return


def users_pagination_menu():

    return ReplyKeyboardMarkup(
        [
            ["⬅️ قبلی", "بعدی ➡️"],
            ["⬅️ برگشت به مدیریت"]
        ],
        resize_keyboard=True
    )

def orders_pagination_menu():

    return ReplyKeyboardMarkup(
        [
            ["⬅️ قبلی", "بعدی ➡️"],
            ["⬅️ برگشت به مدیریت"]
        ],
        resize_keyboard=True
    )
# ================= دریافت رسید =================

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    print("RECEIPT USER:", user_id)
    print("RENEW USERS:", renew_users)


    if user_id == ADMIN_ID:
        return

    if user_id in renew_users:
            
        print("RENEW DATA:", renew_users.get(user_id))


        user_info = await get_user(user_id)

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ تایید تمدید",
                    callback_data=f"renew_ok|{user_id}"
                ),
                InlineKeyboardButton(
                    "❌ رد تمدید",
                    callback_data=f"renew_no|{user_id}"
                )
            ]
        ]


        await context.bot.send_photo(
            chat_id=ADMIN_ID,

            photo=update.message.photo[-1].file_id,

            caption=
            f"🔄 درخواست تمدید اشتراک\n\n"
            f"🆔 User ID: {user_id}\n"
            f"👤 یوزرنیم: @{user_info[0] or 'ندارد'}\n"
            f"👨 نام: {user_info[1] or 'ندارد'}\n\n"
            f"📦 پلن تمدید:\n{renew_users[user_id]['plan']}\n"
            f"💰 مبلغ: {renew_users[user_id]['price']}",

            reply_markup=InlineKeyboardMarkup(buttons)
        )

        await update.message.reply_text(
            "✅ رسید تمدید ارسال شد.\nمنتظر تایید باشید."
        )

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


    user_info = await get_user(user_id)
    
    await context.bot.send_photo(

        chat_id=ADMIN_ID,

        photo=update.message.photo[-1].file_id,

        caption=

        f"📥 رسید جدید\n\n"
        f"🆔 User ID: {user_id}\n"
        f"👤 یوزرنیم: @{user_info[0] or 'ندارد'}\n"
        f"👨 نام: {user_info[1] or 'ندارد'}\n\n"
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
    global renew_users

    query = update.callback_query

    await query.answer()
   
    print("BUTTON CLICKED:", query.data)
 
    action, user_id = query.data.split("|")

    user_id = int(user_id)



    if action == "renew_ok":

        new_date_text = None

        print("USER ID:", user_id)
        print("RENEW USERS:", renew_users)

        if user_id in renew_users:

            old_service = renew_users[user_id]["old_service"]

            old_config = old_service[2]

            from datetime import datetime, timedelta
            from persiantools.jdatetime import JalaliDate


            # تاریخ قبلی
            expire = old_service[3]

            try:
                old_date = datetime.strptime(
                    expire,
                    "%Y-%m-%d"
                ).date()

            except:
                old_date = JalaliDate.strptime(
                    expire,
                    "%Y/%m/%d"
                ).to_gregorian()


            # تمدید از امروز + 30 روز
            new_gregorian = datetime.now().date() + timedelta(days=30)


            new_jalali = JalaliDate.to_jalali(
                new_gregorian
            )


            new_date_text = new_jalali.strftime(
                "%Y/%m/%d"
            )


            await renew_order(
                old_config,
                new_date_text,
                renew_users[user_id]["plan"],
                renew_users[user_id]["price"]
            )


            print("NEW DATE:", new_date_text)


            del renew_users[user_id]


        await context.bot.send_message(
            chat_id=user_id,
            text=
            "✅ تمدید اشتراک شما تایید شد.\n\n"
            f"📅 تاریخ انقضای جدید:\n{new_date_text}"
        )


        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="✅ تمدید کاربر انجام شد."
        )


        return

    elif action == "renew_no":

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ درخواست تمدید شما رد شد."
        )

        return

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