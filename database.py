import aiosqlite


DB_NAME = "vpnone.db"


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


        await db.commit()



async def add_user(user_id, username, first_name):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO users
            (id, username, first_name)

            VALUES (?, ?, ?)
            """,
            (
                user_id,
                username,
                first_name
            )
        )

        await db.commit()



async def add_order(user_id, plan, price):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO orders
            (user_id, plan, price, status)

            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                plan,
                price,
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
            SELECT * FROM orders
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
            SELECT *
            FROM orders
            WHERE user_id = ?
            AND status = 'approved'
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()