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