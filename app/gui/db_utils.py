import asyncio
import aiomysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'albumvision_app')
DB_PASS = os.getenv('DB_PASS', 'AVp@ss_2025!')
DB_NAME = os.getenv('DB_NAME', 'albumvision')


async def db_connect():
    try:
        pool = await aiomysql.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            autocommit=True,
            maxsize=10,
        )
        return pool
    except Exception as e:
        print(f"❌ Could not connect to DB: {e}")
        return None


async def init_db(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS test_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


async def insert_entry(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            entry_name = f"Test Entry {datetime.utcnow().isoformat()}"
            await cur.execute(
                "INSERT INTO test_entries (name) VALUES (%s)", (entry_name,)
            )
            print(f"✅ Inserted! Entry: {entry_name}")


async def fetch_latest(pool):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM test_entries ORDER BY created_at DESC LIMIT 5")
            rows = await cur.fetchall()
            print("📦 Latest entries:", rows)


async def main():
    pool = await db_connect()
    if pool:
        try:
            await init_db(pool)
            await insert_sample(pool)
            await get_latest(pool)
        except Exception as e:
            print(f"❌ DB operation error: {e}")
        finally:
            pool.close()
            await pool.wait_closed()
    else:
        print("⚠️ Skipping DB actions: No live connection.")


if __name__ == '__main__':
    asyncio.run(main())
