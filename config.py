import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "0"))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Stripe fixed payment links
STRIPE_MONTHLY_LINK = os.getenv(
    "STRIPE_MONTHLY_LINK",
    "https://buy.stripe.com/9B68wP6e39dk7Hg4cndnW02",
)
STRIPE_BIWEEKLY_LINK = os.getenv(
    "STRIPE_BIWEEKLY_LINK",
    "https://buy.stripe.com/fZu14n6e3cpw0eOgZ9dnW03",
)

CURRENCY_CODE = os.getenv("CURRENCY_CODE", "USD")
MONTHLY_PRICE = int(os.getenv("MONTHLY_PRICE", "200"))
BIWEEKLY_PRICE = int(os.getenv("BIWEEKLY_PRICE", "140"))

# Subscription durations in days
MONTHLY_DAYS = 30
BIWEEKLY_DAYS = 14
