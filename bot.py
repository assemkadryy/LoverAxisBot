import asyncio
import logging
from datetime import datetime, timedelta, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import config
import database as db
from payments import create_payment_intent, get_payment_status

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Plan descriptions ────────────────────────────────────────────────
PLANS = {
    "monthly": {
        "label": "اشتراك شهري (30 يوم)",
        "price": config.MONTHLY_PRICE,
        "days": config.MONTHLY_DAYS,
    },
    "biweekly": {
        "label": "اشتراك أسبوعين (14 يوم)",
        "price": config.BIWEEKLY_PRICE,
        "days": config.BIWEEKLY_DAYS,
    },
}


# ── /start ───────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            f"⭐ اشتراك شهري – {config.MONTHLY_PRICE} {config.CURRENCY_CODE} ⭐",
            callback_data="plan_monthly",
        )],
        [InlineKeyboardButton(
            f"⭐ اشتراك أسبوعين – {config.BIWEEKLY_PRICE} {config.CURRENCY_CODE} ⭐",
            callback_data="plan_biweekly",
        )],
        [InlineKeyboardButton(
            "👈 تجديد إشتراك المجموعة المميزة",
            callback_data="renew",
        )],
        [InlineKeyboardButton(
            "📌 حالة الاشتراك",
            callback_data="status",
        )],
    ]

    text = "من فضلك اختر أحد الخيارات التالية للإشتراك 👇"

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ── Subscription status ─────────────────────────────────────────────
async def subscription_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    active = await db.get_active_subscription(update.effective_user.id)

    if active:
        end = datetime.fromisoformat(active["end_date"])
        text = (
            "📌 حالة اشتراكك:\n\n"
            f"✅ الاشتراك فعّال\n"
            f"📋 الباقة: {PLANS[active['plan']]['label']}\n"
            f"📅 ينتهي في: {end.strftime('%Y-%m-%d %H:%M UTC')}\n"
        )
    else:
        text = "❌ لا يوجد لديك اشتراك فعّال حالياً.\nاضغط /start للإشتراك."

    await query.edit_message_text(text)


# ── Subscribe / Renew → show plan choices ────────────────────────────
async def show_plans(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(
            f"📅 شهري – {config.MONTHLY_PRICE} {config.CURRENCY_CODE}",
            callback_data="plan_monthly",
        )],
        [InlineKeyboardButton(
            f"📅 أسبوعين – {config.BIWEEKLY_PRICE} {config.CURRENCY_CODE}",
            callback_data="plan_biweekly",
        )],
    ]

    await query.edit_message_text(
        "🔄 اختر الباقة لتجديد الاشتراك 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ── Plan selected → create payment ──────────────────────────────────
async def plan_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("plan_", "")
    plan = PLANS[plan_key]
    user = update.effective_user

    await query.edit_message_text("⏳ جاري إنشاء رابط الدفع...")

    try:
        intent = await create_payment_intent(
            amount=plan["price"],
            currency=config.CURRENCY_CODE,
            message=f"المجموعة المميزة – {plan['label']}",
        )
    except Exception as e:
        logger.error("Ziina error: %s", e)
        await query.edit_message_text(
            "❌ فشل إنشاء رابط الدفع. حاول مرة أخرى لاحقاً."
        )
        return

    # Save to database
    await db.create_subscription(
        user_id=user.id,
        username=user.username or user.full_name,
        plan=plan_key,
        price=plan["price"],
        currency=config.CURRENCY_CODE,
        payment_intent_id=intent["id"],
    )

    keyboard = [
        [InlineKeyboardButton("💳 ادفع الآن", url=intent["redirect_url"])],
        [InlineKeyboardButton("✅ دفعت – تحقق من الدفع",
                              callback_data=f"check_{intent['id']}")],
    ]

    await query.edit_message_text(
        f"*{plan['label']}*\n"
        f"المبلغ: *{plan['price']} {config.CURRENCY_CODE}*\n\n"
        "اضغط على الزر أدناه للدفع.\n"
        "بعد الدفع اضغط \"دفعت\" لاستلام رابط الدخول.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ── Check payment status ────────────────────────────────────────────
async def check_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    payment_id = query.data.replace("check_", "")

    sub = await db.get_subscription_by_payment(payment_id)
    if not sub:
        await query.edit_message_text("❌ لم يتم العثور على الاشتراك.")
        return

    if sub["payment_status"] == "completed":
        await query.edit_message_text(
            f"✅ تم التفعيل مسبقاً!\nرابط الدخول: {sub['invite_link']}"
        )
        return

    try:
        status = await get_payment_status(payment_id)
    except Exception as e:
        logger.error("Ziina status check error: %s", e)
        await query.edit_message_text(
            "❌ لم نتمكن من التحقق من الدفع. حاول مرة أخرى بعد قليل."
        )
        return

    if status == "completed":
        await _activate_subscription(sub, payment_id, query, ctx)
    elif status in ("failed", "canceled"):
        await db.update_payment_status(payment_id, status)
        await query.edit_message_text(
            "❌ فشل الدفع أو تم إلغاؤه.\nاضغط /start للمحاولة مرة أخرى."
        )
    else:
        keyboard = [
            [InlineKeyboardButton("✅ دفعت – تحقق مرة أخرى",
                                  callback_data=f"check_{payment_id}")],
        ]
        await query.edit_message_text(
            "⏳ لم يتم تأكيد الدفع بعد.\n"
            "أكمل الدفع ثم اضغط الزر مرة أخرى.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def _activate_subscription(sub: dict, payment_id: str, query, ctx):
    plan = PLANS[sub["plan"]]
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=plan["days"])

    # Create single-use invite link
    try:
        invite = await ctx.bot.create_chat_invite_link(
            chat_id=config.TELEGRAM_GROUP_ID,
            member_limit=1,
            expire_date=int((now + timedelta(hours=24)).timestamp()),
            name=f"sub_{sub['user_id']}_{payment_id[:8]}",
        )
        invite_url = invite.invite_link
    except Exception as e:
        logger.error("Failed to create invite link: %s", e)
        await query.edit_message_text(
            "❌ تم تأكيد الدفع لكن فشل إنشاء رابط الدخول.\n"
            "تواصل مع المسؤول."
        )
        return

    await db.activate_subscription(
        payment_intent_id=payment_id,
        start_date=now.isoformat(),
        end_date=end.isoformat(),
        invite_link=invite_url,
    )

    await query.edit_message_text(
        f"✅ تم تأكيد الدفع بنجاح!\n\n"
        f"📋 الباقة: {plan['label']}\n"
        f"📅 فعّال حتى: {end.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"🔗 رابط دخول المجموعة: {invite_url}\n\n"
        "⚠️ هذا الرابط للاستخدام مرة واحدة وينتهي خلال 24 ساعة.",
    )

    # Notify admin
    try:
        user = query.from_user
        await ctx.bot.send_message(
            chat_id=config.ADMIN_USER_ID,
            text=(
                f"💰 اشتراك جديد!\n"
                f"المستخدم: @{user.username or user.full_name} (ID: {user.id})\n"
                f"الباقة: {plan['label']}\n"
                f"المبلغ: {sub['price']} {sub['currency']}\n"
                f"ينتهي: {end.strftime('%Y-%m-%d %H:%M UTC')}"
            ),
        )
    except Exception:
        pass


# ── Scheduled job: remove expired members ────────────────────────────
async def remove_expired_members(ctx: ContextTypes.DEFAULT_TYPE):
    expired = await db.get_expired_subscriptions()
    for sub in expired:
        try:
            await ctx.bot.ban_chat_member(
                chat_id=config.TELEGRAM_GROUP_ID,
                user_id=sub["user_id"],
                revoke_messages=False,
            )
            # Immediately unban so they can re-subscribe later
            await ctx.bot.unban_chat_member(
                chat_id=config.TELEGRAM_GROUP_ID,
                user_id=sub["user_id"],
                only_if_banned=True,
            )
            await db.mark_expired(sub["id"])
            logger.info("Removed expired member %s", sub["user_id"])

            # Notify the user
            try:
                await ctx.bot.send_message(
                    chat_id=sub["user_id"],
                    text=(
                        "⏰ انتهى اشتراكك وتم إزالتك من المجموعة.\n\n"
                        "اضغط /start للإشتراك مرة أخرى!"
                    ),
                )
            except Exception:
                pass

        except Exception as e:
            logger.error("Failed to remove user %s: %s", sub["user_id"], e)


# ── Auto-poll pending payments ───────────────────────────────────────
async def poll_pending_payments(ctx: ContextTypes.DEFAULT_TYPE):
    pending = await db.get_pending_subscriptions()
    for sub in pending:
        try:
            status = await get_payment_status(sub["payment_intent_id"])
        except Exception:
            continue

        if status == "completed":
            plan = PLANS[sub["plan"]]
            now = datetime.now(timezone.utc)
            end = now + timedelta(days=plan["days"])

            try:
                invite = await ctx.bot.create_chat_invite_link(
                    chat_id=config.TELEGRAM_GROUP_ID,
                    member_limit=1,
                    expire_date=int((now + timedelta(hours=24)).timestamp()),
                    name=f"sub_{sub['user_id']}_{sub['payment_intent_id'][:8]}",
                )
                invite_url = invite.invite_link
            except Exception as e:
                logger.error("Invite link error in poller: %s", e)
                continue

            await db.activate_subscription(
                payment_intent_id=sub["payment_intent_id"],
                start_date=now.isoformat(),
                end_date=end.isoformat(),
                invite_link=invite_url,
            )

            try:
                await ctx.bot.send_message(
                    chat_id=sub["user_id"],
                    text=(
                        f"✅ تم تأكيد الدفع بنجاح!\n\n"
                        f"📋 الباقة: {plan['label']}\n"
                        f"📅 فعّال حتى: {end.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                        f"🔗 رابط دخول المجموعة: {invite_url}\n\n"
                        "⚠️ هذا الرابط للاستخدام مرة واحدة وينتهي خلال 24 ساعة."
                    ),
                )
            except Exception as e:
                logger.error("Failed to notify user %s: %s", sub["user_id"], e)

        elif status in ("failed", "canceled"):
            await db.update_payment_status(sub["payment_intent_id"], status)


# ── Main ─────────────────────────────────────────────────────────────
def main():
    asyncio.get_event_loop().run_until_complete(db.init_db())

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans,
                                         pattern=r"^renew$"))
    app.add_handler(CallbackQueryHandler(plan_selected,
                                         pattern=r"^plan_"))
    app.add_handler(CallbackQueryHandler(check_payment,
                                         pattern=r"^check_"))
    app.add_handler(CallbackQueryHandler(subscription_status,
                                         pattern=r"^status$"))

    # Scheduled jobs
    job_queue = app.job_queue
    # Check for expired subscriptions every hour
    job_queue.run_repeating(remove_expired_members, interval=3600, first=10)
    # Poll pending payments every 30 seconds
    job_queue.run_repeating(poll_pending_payments, interval=30, first=5)

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
