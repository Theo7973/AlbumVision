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
    

async def fetch_latest(pool):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM albums ORDER BY created_at DESC LIMIT 5")
            rows = await cur.fetchall()
            print("📦 Latest entries:", rows)

async def print_row_by_id(pool, row_id):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM images WHERE id = %s", (row_id,))
            row = await cur.fetchone()
            if row:
                print("🔎 Row found:", row)
            else:
                print(f"❌ No row found with id {row_id}")

async def insert_image_metadata(
    pool,
    file_path,
    orig_filename,
    detected_dt,
    width_px,
    height_px,
    phash,
    created_at,
    captured_dt,
    make,
    model,
    format,
    mode,
    size
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = """
                INSERT INTO images
                (file_path, orig_filename, detected_dt, width_px, height_px, phash, created_at, captured_dt, make, model, format, mode, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            await cur.execute(sql, (
                file_path,
                orig_filename,
                detected_dt,
                width_px,
                height_px,
                phash,
                created_at,
                captured_dt,
                make,
                model,
                format,
                mode,
                size
            ))
            await conn.commit()
            print(f"✅ Inserted metadata for file: {orig_filename}")

async def main():
    pool = await db_connect()
    if pool:
        try:
            await insert_image_metadata(
            pool,
            "/path/to/test2.jpg",
            "test2.jpg",
            datetime.now(),
            1920,
            1080,
            "1234567890abcdef",
            datetime.now(),
            datetime.now(),
            "Canon",
            "EOS 80D",
            "JPEG",
            "RGB",
            2048000
        )
        except Exception as e:
            print(f"❌ DB operation error: {e}")
        finally:
            pool.close()
            await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
    # Example usage of print_row_by_id
    # asyncio.run(print_row_by_id(pool, 1))  # Replace 1 with the desired row ID