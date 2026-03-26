import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "0"))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

ZIINA_API_TOKEN = os.getenv("ZIINA_API_TOKEN")
ZIINA_API_BASE = "https://api-v2.ziina.com/api"
ZIINA_TEST_MODE = os.getenv("ZIINA_TEST_MODE", "true").lower() == "true"

CURRENCY_CODE = os.getenv("CURRENCY_CODE", "USD")
MONTHLY_PRICE = int(os.getenv("MONTHLY_PRICE", "200"))
BIWEEKLY_PRICE = int(os.getenv("BIWEEKLY_PRICE", "140"))

# Subscription durations in days
MONTHLY_DAYS = 30
BIWEEKLY_DAYS = 14
