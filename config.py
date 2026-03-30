import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "0"))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_MONTHLY_PRICE_ID = os.getenv("STRIPE_MONTHLY_PRICE_ID", "price_1TGKopHCTz1eqMMVl7krAf8d")
STRIPE_BIWEEKLY_PRICE_ID = os.getenv("STRIPE_BIWEEKLY_PRICE_ID", "price_1TGKumHCTz1eqMMVh8eiTQZV")

# Display prices
CURRENCY_CODE = os.getenv("CURRENCY_CODE", "USD")
MONTHLY_PRICE = int(os.getenv("MONTHLY_PRICE", "230"))
BIWEEKLY_PRICE = int(os.getenv("BIWEEKLY_PRICE", "140"))

# Stripe amounts in cents (230 USD = 23000, 140 USD = 14000)
MONTHLY_AMOUNT = int(os.getenv("MONTHLY_AMOUNT", "23000"))
BIWEEKLY_AMOUNT = int(os.getenv("BIWEEKLY_AMOUNT", "14000"))

# Subscription durations in days
MONTHLY_DAYS = 30
BIWEEKLY_DAYS = 14

# Public URL of this server (Railway domain)
PUBLIC_URL = os.getenv("PUBLIC_URL", "")

# Webhook server port (Railway sets PORT automatically)
PORT = int(os.getenv("PORT", "8080"))
