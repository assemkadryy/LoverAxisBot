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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PLANS = {
    "monthly": {
        "label": "اشتراك شهري (30 يوم)",
        "price": config.MONTHLY_PRICE,
        "days": config.MONTHLY_DAYS,
        "link": config.STRIPE_MONTHLY_LINK,
    },
    "biweekly": {
        "label": "اشتراك أسبوعين (14 يوم)",
        "price": config.BIWEEKLY_PRICE,
        "days": config.BIWEEKLY_DAYS,
        "link": config.STRIPE_BIWEEKLY_LINK,
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

    await update.message.reply_text(
        "من فضلك اختر أحد الخيارات التالية للإشتراك 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ── Subscription status ──────────────────────────────────────────────
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


# ── Renew → show plan choices ────────────────────────────────────────
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


# ── Plan selected → send Stripe link ────────────────────────────────
async def plan_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("plan_", "")
    plan = PLANS[plan_key]
    user = update.effective_user

    await db.create_subscription(
        user_id=user.id,
        username=user.username or user.full_name,
        plan=plan_key,
        price=plan["price"],
        currency=config.CURRENCY_CODE,
    )

    keyboard = [
        [InlineKeyboardButton("💳 ادفع الآن", url=plan["link"])],
        [InlineKeyboardButton(
            "✅ دفعت – أرسل طلب التفعيل",
            callback_data=f"paid_{plan_key}_{user.id}",
        )],
    ]

    await query.edit_message_text(
        f"*{plan['label']}*\n"
        f"المبلغ: *{plan['price']} {config.CURRENCY_CODE}*\n\n"
        "اضغط على زر الدفع وأكمل العملية عبر Stripe.\n"
        "بعد إتمام الدفع اضغط \"دفعت\" لإرسال طلب التفعيل.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ── User claims payment → notify admin ──────────────────────────────
async def payment_claimed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    plan_key = parts[1]
    user = query.from_user
    plan = PLANS[plan_key]

    await query.edit_message_text(
        "⏳ تم إرسال طلبك!\n"
        "سيتم مراجعة الدفع وتفعيل اشتراكك خلال دقائق."
    )

    keyboard = [
        [InlineKeyboardButton(
            "✅ تأكيد وتفعيل الاشتراك",
            callback_data=f"confirm_{user.id}_{plan_key}",
        )],
        [InlineKeyboardButton(
            "❌ رفض",
            callback_data=f"reject_{user.id}",
        )],
    ]

    await ctx.bot.send_message(
        chat_id=config.ADMIN_USER_ID,
        text=(
            f"🔔 طلب تفعيل اشتراك جديد!\n\n"
            f"المستخدم: @{user.username or user.full_name}\n"
            f"ID: `{user.id}`\n"
            f"الباقة: {plan['label']}\n"
            f"المبلغ: {plan['price']} {config.CURRENCY_CODE}\n\n"
            "هل تم الدفع؟"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ── Admin confirms → activate + send invite link ─────────────────────
async def admin_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != config.ADMIN_USER_ID:
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return

    await query.answer()

    parts = query.data.split("_", 2)
    user_id = int(parts[1])
    plan_key = parts[2]
    plan = PLANS[plan_key]
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=plan["days"])

    try:
        invite = await ctx.bot.create_chat_invite_link(
            chat_id=config.TELEGRAM_GROUP_ID,
            member_limit=1,
            expire_date=int((now + timedelta(hours=24)).timestamp()),
            name=f"sub_{user_id}_{int(now.timestamp())}",
        )
        invite_url = invite.invite_link
    except Exception as e:
        logger.error("Failed to create invite link: %s", e)
        await query.edit_message_text("❌ فشل إنشاء رابط الدخول. حاول مرة أخرى.")
        return

    await db.activate_subscription_by_user(
        user_id=user_id,
        plan=plan_key,
        start_date=now.isoformat(),
        end_date=end.isoformat(),
        invite_link=invite_url,
    )

    await query.edit_message_text(
        f"✅ تم تفعيل اشتراك المستخدم {user_id}\n"
        f"الباقة: {plan['label']}\n"
        f"ينتهي: {end.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    await ctx.bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ تم تأكيد دفعك وتفعيل اشتراكك!\n\n"
            f"📋 الباقة: {plan['label']}\n"
            f"📅 فعّال حتى: {end.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"🔗 رابط دخول المجموعة: {invite_url}\n\n"
            "⚠️ هذا الرابط للاستخدام مرة واحدة وينتهي خلال 24 ساعة."
        ),
    )


# ── Admin rejects ────────────────────────────────────────────────────
async def admin_reject(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != config.ADMIN_USER_ID:
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return

    await query.answer()

    user_id = int(query.data.split("_")[1])

    await query.edit_message_text(f"❌ تم رفض طلب المستخدم {user_id}.")

    await ctx.bot.send_message(
        chat_id=user_id,
        text=(
            "❌ لم يتم التحقق من دفعك.\n"
            "تأكد من إتمام عملية الدفع وأرسل طلبك مرة أخرى.\n"
            "اضغط /start للمحاولة مرة أخرى."
        ),
    )


# ── Scheduled job: remove expired members ───────────────────────────
async def remove_expired_members(ctx: ContextTypes.DEFAULT_TYPE):
    expired = await db.get_expired_subscriptions()
    for sub in expired:
        try:
            await ctx.bot.ban_chat_member(
                chat_id=config.TELEGRAM_GROUP_ID,
                user_id=sub["user_id"],
                revoke_messages=False,
            )
            await ctx.bot.unban_chat_member(
                chat_id=config.TELEGRAM_GROUP_ID,
                user_id=sub["user_id"],
                only_if_banned=True,
            )
            await db.mark_expired(sub["id"])
            logger.info("Removed expired member %s", sub["user_id"])

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


# ── Main ─────────────────────────────────────────────────────────────
def main():
    asyncio.get_event_loop().run_until_complete(db.init_db())

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans,          pattern=r"^renew$"))
    app.add_handler(CallbackQueryHandler(plan_selected,       pattern=r"^plan_"))
    app.add_handler(CallbackQueryHandler(payment_claimed,     pattern=r"^paid_"))
    app.add_handler(CallbackQueryHandler(admin_confirm,       pattern=r"^confirm_"))
    app.add_handler(CallbackQueryHandler(admin_reject,        pattern=r"^reject_"))
    app.add_handler(CallbackQueryHandler(subscription_status, pattern=r"^status$"))

    job_queue = app.job_queue
    job_queue.run_repeating(remove_expired_members, interval=3600, first=10)

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
