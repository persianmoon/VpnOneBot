import os
import aiosqlite
from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDate

print("DATABASE VERSION NEW")


DB_NAME = "/data/vpnone.db"


async def init_db():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            price TEXT,
            status TEXT
        )
        """)


        try:
            await db.execute(
                "ALTER TABLE orders ADD COLUMN config TEXT"
            )
        except:
            pass

        try:
            await db.execute(
                "ALTER TABLE orders ADD COLUMN expire_date TEXT"
            )
        except:
            pass
        
        
        try:
            await db.execute(
                "ALTER TABLE orders ADD COLUMN buy_date TEXT"
            )
        except:
            pass

        await db.commit()


        # ساخت جدول سفارشات
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            price TEXT,
            status TEXT

        )
        """)


        try:
            await db.execute(
                "ALTER TABLE orders ADD COLUMN config TEXT"
            )
        except:
            pass


        try:
            await db.execute(
                "ALTER TABLE orders ADD COLUMN expire_date TEXT"
            )
        except:
            pass

        
        await db.commit()
        print("DATABASE INITIALIZED")



async def add_user(user_id, username, first_name):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO users
            (id, username, first_name)

            VALUES (?, ?, ?)

            ON CONFLICT(id) DO UPDATE SET

            username = excluded.username,
            first_name = excluded.first_name

            """,
            (
                user_id,
                username,
                first_name
            )
        )

        await db.commit()



async def add_order(user_id, plan, price):
    
    print("ADD ORDER RUNNING")

    from persiantools.jdatetime import JalaliDate
    from datetime import datetime, timedelta

    buy_date = JalaliDate.today().strftime("%Y/%m/%d")

    expire_date = JalaliDate(
        datetime.now() + timedelta(days=30)
    ).strftime("%Y/%m/%d")


    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO orders
            (
                user_id,
                plan,
                price,
                config,
                buy_date,
                expire_date,
                status
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                plan,
                config,
                price,
                buy_date,
                expire_date,
                "pending"
            )
        )

        await db.commit()



async def get_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM users ORDER BY id DESC"
        )

        return await cursor.fetchall()



async def get_orders():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM orders ORDER BY id DESC"
        )

        return await cursor.fetchall()



async def get_pending_orders():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM orders
            WHERE status='pending'
            ORDER BY id DESC
            """
        )

        return await cursor.fetchall()



async def get_sales_count():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE status='approved'
            """
        )

        result = await cursor.fetchone()

        return result[0]



async def update_order_status(user_id, status):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE orders

            SET status = ?

            WHERE id = (

                SELECT id
                FROM orders
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 1

            )

            """,
            (
                status,
                user_id
            )
        )

        await db.commit()


async def renew_order(order_config, new_expire_date, new_plan, new_price):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE orders

            SET
                plan = ?,
                price = ?,
                expire_date = ?,
                status = 'approved'

            WHERE config = ?

            """,
            (
                new_plan,
                new_price,
                new_expire_date,
                order_config
            )
        )

        print("RENEW UPDATED ROWS:", db.total_changes)

        await db.commit()


async def get_user_orders(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()



async def get_user_active_orders(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                plan,
                price,
                config,
                expire_date

            FROM orders

            WHERE user_id = ?
            AND status = 'approved'

            ORDER BY id DESC

            """,
            (user_id,)
        )

        result = await cursor.fetchall()

        print("USER ID:", user_id)
        print("ACTIVE ORDERS:", result)

        print("ACTIVE SERVICE RESULT:", result)
        return result


async def save_user_service(
    user_id,
    plan,
    price,
    config,
    buy_date,
    expire_date,
    username=None,
    first_name=None,
    status="approved"
):

    print("SAVE SERVICE RUNNING")

    async with aiosqlite.connect(DB_NAME) as db:

        # اول چک می‌کنیم سفارش تایید شده دارد یا نه
        cursor = await db.execute(
            """
            SELECT id
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        order = await cursor.fetchone()


        if order:

            await db.execute(
                """
                UPDATE orders
                SET
                    plan = ?,
                    price = ?,
                    config = ?,
                    expire_date = ?,
                    status = 'approved'

                WHERE id = ?
                """,
                (
                    plan,
                    price,
                    config,
                    expire_date,
                    order[0]
                )
            )


        else:

            await db.execute(
                """
                INSERT INTO orders
                (
                    user_id,
                    plan,
                    price,
                    config,
                    buy_date,
                    expire_date,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    plan,
                    price,
                    buy_date,
                    config,
                    expire_date,
                    "approved"
                )
            )


        await db.execute(
            """
            INSERT OR IGNORE INTO users
            (
                id,
                username,
                first_name
            )

            VALUES (?, ?, ?)
            """,
            (
                user_id,
                username,
                first_name
            )
        )


        await db.commit()


        
async def get_user_active_service(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT plan, price, config, expire_date
            FROM orders
            WHERE user_id = ?
            AND status = 'approved'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        return await cursor.fetchone()
    
async def delete_user(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        await db.execute(
            "DELETE FROM orders WHERE user_id = ?",
            (user_id,)
        )

        await db.commit()
        
        
async def delete_users(user_ids):

    async with aiosqlite.connect(DB_NAME) as db:

        for user_id in user_ids:

            await db.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )

            await db.execute(
                "DELETE FROM orders WHERE user_id = ?",
                (user_id,)
            )

        await db.commit()


async def get_user(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT username, first_name
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )

        return await cursor.fetchone()
    
    
    
async def delete_order(order_id):

    async with aiosqlite.connect(DB_NAME) as db:

        # حذف سفارش
        await db.execute(
            """
            DELETE FROM orders
            WHERE id = ?
            AND status != 'approved'
            """,
            (order_id,)
        )

        # گرفتن سفارش‌های باقی مانده
        cursor = await db.execute(
            "SELECT id FROM orders ORDER BY id"
        )

        orders = await cursor.fetchall()


        # مرتب کردن شماره‌ها
        new_id = 1

        for order in orders:

            await db.execute(
                "UPDATE orders SET id = ? WHERE id = ?",
                (new_id, order[0])
            )

            new_id += 1


        # تنظیم شماره سفارش بعدی
        await db.execute(
            "DELETE FROM sqlite_sequence WHERE name='orders'"
        )

        await db.execute(
            "INSERT INTO sqlite_sequence(name, seq) VALUES('orders', ?)",
            (new_id - 1,)
        )


        await db.commit()
        
        
        
async def delete_all_orders():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM orders
            WHERE status != 'approved'
            """
        )

        await db.execute(
            "DELETE FROM sqlite_sequence WHERE name='orders'"
        )

        await db.commit()
        
        
async def toggle_order_status(order_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT status
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        )

        order = await cursor.fetchone()

        if not order:
            return None


        new_status = (
            "approved"
            if order[0] == "pending"
            else "pending"
        )


        await db.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            """,
            (
                new_status,
                order_id
            )
        )

        await db.commit()

        return new_status