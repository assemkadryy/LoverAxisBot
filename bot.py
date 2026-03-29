import asyncio
import logging
from datetime import datetime, timedelta, timezone

import stripe
from aiohttp import web
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

stripe.api_key = config.STRIPE_SECRET_KEY

PLANS = {
    "monthly": {
        "label": "اشتراك شهري (30 يوم)",
        "price": config.MONTHLY_PRICE,
        "price_id": config.STRIPE_MONTHLY_PRICE_ID,
        "days": config.MONTHLY_DAYS,
    },
    "biweekly": {
        "label": "اشتراك أسبوعين (14 يوم)",
        "price": config.BIWEEKLY_PRICE,
        "price_id": config.STRIPE_BIWEEKLY_PRICE_ID,
        "days": config.BIWEEKLY_DAYS,
    },
    "test": {
        "label": "اشتراك تجريبي (3 دقائق)",
        "price": 1,
        "currency": "AED",
        "price_id": config.STRIPE_TEST_PRICE_ID,
        "days": None,
        "minutes": 3,
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

    if config.STRIPE_TEST_PRICE_ID:
        keyboard.insert(2, [InlineKeyboardButton(
            "🧪 اشتراك تجريبي – 1 AED (3 دقائق)",
            callback_data="plan_test",
        )])

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


# ── Plan selected → create Stripe session ───────────────────────────
async def plan_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("plan_", "")
    plan = PLANS[plan_key]
    user = update.effective_user

    await query.edit_message_text("⏳ جاري إنشاء رابط الدفع...")

    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                "price": plan["price_id"],
                "quantity": 1,
            }],
            mode="payment",
            client_reference_id=str(user.id),
            metadata={"plan": plan_key},
            success_url=(
                f"{config.PUBLIC_URL}/payment/success"
                f"?bot={config.TELEGRAM_BOT_USERNAME}"
            ),
            cancel_url=(
                f"{config.PUBLIC_URL}/payment/cancel"
                f"?bot={config.TELEGRAM_BOT_USERNAME}"
            ),
            expires_at=int(
                (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
            ),
        )
    except Exception as e:
        logger.error("Stripe session error: %s", e)
        await query.edit_message_text(
            "❌ فشل إنشاء رابط الدفع. حاول مرة أخرى لاحقاً."
        )
        return

    await db.create_subscription(
        user_id=user.id,
        username=user.username or user.full_name,
        plan=plan_key,
        price=plan["price"],
        currency=config.CURRENCY_CODE,
        stripe_session_id=session.id,
    )

    display_currency = plan.get("currency", config.CURRENCY_CODE)
    await query.edit_message_text(
        f"*{plan['label']}*\n"
        f"المبلغ: *{plan['price']} {display_currency}*\n\n"
        "اضغط الزر أدناه للدفع.\n"
        "سيصلك رابط الدخول تلقائياً بعد إتمام الدفع ✅\n\n"
        "⏰ الرابط صالح لمدة ساعة واحدة.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 ادفع الآن", url=session.url)],
        ]),
        parse_mode="Markdown",
    )


# ── Activate subscription and notify user ───────────────────────────
async def activate_and_notify(bot, user_id: int, plan_key: str):
    plan = PLANS[plan_key]
    now = datetime.now(timezone.utc)
    if plan.get("minutes"):
        end = now + timedelta(minutes=plan["minutes"])
    else:
        end = now + timedelta(days=plan["days"])

    try:
        invite = await bot.create_chat_invite_link(
            chat_id=config.TELEGRAM_GROUP_ID,
            member_limit=1,
            expire_date=int((now + timedelta(hours=24)).timestamp()),
            name=f"sub_{user_id}_{int(now.timestamp())}",
        )
        invite_url = invite.invite_link
    except Exception as e:
        logger.error("Failed to create invite link for %s: %s", user_id, e)
        return

    await db.activate_subscription_by_user(
        user_id=user_id,
        plan=plan_key,
        start_date=now.isoformat(),
        end_date=end.isoformat(),
        invite_link=invite_url,
    )

    await bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ تم تأكيد دفعك وتفعيل اشتراكك!\n\n"
            f"📋 الباقة: {plan['label']}\n"
            f"📅 فعّال حتى: {end.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"🔗 رابط دخول المجموعة: {invite_url}\n\n"
            "⚠️ هذا الرابط للاستخدام مرة واحدة وينتهي خلال 24 ساعة."
        ),
    )

    try:
        await bot.send_message(
            chat_id=config.ADMIN_USER_ID,
            text=(
                f"💰 اشتراك جديد!\n"
                f"المستخدم ID: {user_id}\n"
                f"الباقة: {plan['label']}\n"
                f"ينتهي: {end.strftime('%Y-%m-%d %H:%M UTC')}"
            ),
        )
    except Exception:
        pass


# ── Stripe webhook handler ───────────────────────────────────────────
def make_webhook_handler(bot):
    async def handle_stripe_webhook(request: web.Request) -> web.Response:
        payload = await request.read()
        sig = request.headers.get("Stripe-Signature", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig, config.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return web.Response(status=400, text="Invalid signature")
        except Exception as e:
            logger.error("Webhook parse error: %s", e)
            return web.Response(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = int(session.get("client_reference_id", 0))
            plan_key = session.get("metadata", {}).get("plan")
            session_id = session.get("id")

            if not user_id or not plan_key:
                logger.warning("Missing user_id or plan in webhook: %s", session_id)
                return web.Response(status=200)

            # Verify session exists in our DB
            sub = await db.get_pending_by_session(session_id)
            if not sub:
                logger.warning("No pending subscription for session: %s", session_id)
                return web.Response(status=200)

            await activate_and_notify(bot, user_id, plan_key)
            logger.info("Activated subscription for user %s plan %s", user_id, plan_key)

        return web.Response(status=200, text="OK")

    return handle_stripe_webhook


# ── Success / Cancel pages ───────────────────────────────────────────
async def payment_success(request: web.Request) -> web.Response:
    bot_username = request.rel_url.query.get("bot", "")
    html = f"""
    <html><body style="font-family:sans-serif;text-align:center;padding:60px">
    <h2>✅ تم الدفع بنجاح!</h2>
    <p>سيصلك رابط الدخول على تيليجرام خلال لحظات.</p>
    {"<br><a href='https://t.me/" + bot_username + "'>العودة للبوت</a>" if bot_username else ""}
    </body></html>
    """
    return web.Response(text=html, content_type="text/html")


async def payment_cancel(request: web.Request) -> web.Response:
    bot_username = request.rel_url.query.get("bot", "")
    html = f"""
    <html><body style="font-family:sans-serif;text-align:center;padding:60px">
    <h2>❌ تم إلغاء الدفع</h2>
    <p>يمكنك المحاولة مرة أخرى من البوت.</p>
    {"<br><a href='https://t.me/" + bot_username + "'>العودة للبوت</a>" if bot_username else ""}
    </body></html>
    """
    return web.Response(text=html, content_type="text/html")


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
async def main_async():
    await db.init_db()

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans,          pattern=r"^renew$"))
    app.add_handler(CallbackQueryHandler(plan_selected,       pattern=r"^plan_"))
    app.add_handler(CallbackQueryHandler(subscription_status, pattern=r"^status$"))

    app.job_queue.run_repeating(remove_expired_members, interval=60, first=10)

    # aiohttp web server
    web_app = web.Application()
    web_app.router.add_post("/webhook/stripe", make_webhook_handler(app.bot))
    web_app.router.add_get("/payment/success", payment_success)
    web_app.router.add_get("/payment/cancel", payment_cancel)
    web_app.router.add_get("/health", lambda r: web.Response(text="OK"))

    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", config.PORT).start()
    logger.info("Webhook server on port %s", config.PORT)

    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Bot started!")
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()

    await runner.cleanup()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
