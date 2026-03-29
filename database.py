import os
from typing import Dict, List, Optional

import aiosqlite
from datetime import datetime, timezone

DB_PATH = os.getenv("DATABASE_PATH", "subscriptions.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                plan TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_status TEXT DEFAULT 'pending',
                start_date TEXT,
                end_date TEXT,
                invite_link TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_subscription(user_id: int, username: str, plan: str,
                              price: float, currency: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO subscriptions
               (user_id, username, plan, price, currency, payment_status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
            (user_id, username, plan, price, currency,
             datetime.now(timezone.utc).isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def activate_subscription_by_user(user_id: int, plan: str,
                                        start_date: str, end_date: str,
                                        invite_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE subscriptions
               SET payment_status = 'completed',
                   plan = ?, start_date = ?, end_date = ?, invite_link = ?
               WHERE user_id = ? AND payment_status = 'pending'""",
            (plan, start_date, end_date, invite_link, user_id)
        )
        await db.commit()


async def get_expired_subscriptions() -> List[Dict]:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM subscriptions
               WHERE payment_status = 'completed' AND end_date < ?""",
            (now,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def mark_expired(subscription_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE subscriptions SET payment_status = 'expired' WHERE id = ?",
            (subscription_id,)
        )
        await db.commit()


async def get_active_subscription(user_id: int) -> Optional[Dict]:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM subscriptions
               WHERE user_id = ? AND payment_status = 'completed'
                     AND end_date >= ?
               ORDER BY end_date DESC LIMIT 1""",
            (user_id, now)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
