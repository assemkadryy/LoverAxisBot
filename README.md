# Telegram Subscription Bot

A Telegram bot for managing premium group subscriptions with Stripe payment integration.

---

## Features

- Monthly (30 days) and two-week (14 days) subscription plans
- Secure payment via Stripe fixed payment links
- Automatically sends group invite link after admin confirms payment
- Automatically removes members when subscription expires
- Admin panel to confirm or reject subscription requests
- Users can check their subscription status anytime

---

## Requirements

- Python 3.11+
- Telegram Bot token (from @BotFather)
- Stripe account with payment links
- Railway account (for deployment)

---

## Local Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=-1001234567890
ADMIN_USER_ID=123456789
STRIPE_MONTHLY_LINK=https://buy.stripe.com/...
STRIPE_BIWEEKLY_LINK=https://buy.stripe.com/...
CURRENCY_CODE=USD
MONTHLY_PRICE=230
BIWEEKLY_PRICE=140
DATABASE_PATH=subscriptions.db
```

### 3. Run the bot

```bash
python3 bot.py
```

---

## Deploy on Railway

1. Push files to GitHub
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **New Project → Deploy from GitHub Repo**
4. Add a **Volume** with mount path `/data`
5. Add environment variables under the **Variables** tab:

| Variable | Value |
|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_GROUP_ID` | Your group ID |
| `ADMIN_USER_ID` | Your Telegram user ID |
| `STRIPE_MONTHLY_LINK` | Stripe link for monthly plan |
| `STRIPE_BIWEEKLY_LINK` | Stripe link for two-week plan |
| `CURRENCY_CODE` | `USD` |
| `MONTHLY_PRICE` | `230` |
| `BIWEEKLY_PRICE` | `140` |
| `DATABASE_PATH` | `/data/subscriptions.db` |

6. Click **Deploy**

---

## How It Works

```
User presses /start
        ↓
Selects a plan (monthly or two-week)
        ↓
Clicks "Pay Now" → redirected to Stripe payment page
        ↓
Completes payment → clicks "I've Paid"
        ↓
Admin receives a notification with Confirm / Reject buttons
        ↓
Admin clicks Confirm → invite link sent to user automatically
        ↓
When subscription expires → user is removed from the group automatically
```

---

## Bot Permissions in the Group

The bot must be an admin in the group with these permissions enabled:
- **Invite users via link**
- **Ban users**

---

## File Structure

| File | Purpose |
|------|---------|
| `bot.py` | Main bot logic |
| `config.py` | Environment variable loader |
| `database.py` | SQLite database layer |
| `requirements.txt` | Python dependencies |
| `Procfile` | Railway start command |
| `runtime.txt` | Python version |
