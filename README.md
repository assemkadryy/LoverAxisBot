# 🤖 Telegram Subscription Bot

> A production-ready Telegram bot for managing premium group subscriptions with automated Stripe payment handling, invite link generation, and subscription lifecycle management.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💳 **Stripe Payments** | Fixed payment links for seamless checkout |
| 📅 **Flexible Plans** | Monthly (30 days) and two-week (14 days) options |
| 🔗 **Auto Invite Links** | Single-use group invite links sent after confirmation |
| ⏰ **Auto Expiry** | Members removed automatically when subscription ends |
| 🛡️ **Admin Control** | Confirm or reject payment requests via inline buttons |
| 📌 **Status Check** | Users can view their active subscription at any time |
| 🔄 **Renewal Support** | Easy subscription renewal flow |

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Bot Framework:** [python-telegram-bot](https://github.com/python-tg/python-telegram-bot) v21
- **Database:** SQLite via `aiosqlite`
- **Payments:** Stripe (fixed payment links)
- **Hosting:** Railway
- **Scheduler:** APScheduler

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot token — get one from [@BotFather](https://t.me/BotFather)
- Stripe account with two payment links created
- The bot must be **admin** in your Telegram group

### 1️⃣ Clone & Install

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

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

### 3️⃣ Run

```bash
python3 bot.py
```

---

## ☁️ Deploy on Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → sign in with GitHub
3. Click **New Project → Deploy from GitHub Repo** → select your repo
4. Add a **Volume** → set mount path to `/data`
5. Go to **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_GROUP_ID` | Your Telegram group ID |
| `ADMIN_USER_ID` | Your personal Telegram user ID |
| `STRIPE_MONTHLY_LINK` | Stripe link for the monthly plan |
| `STRIPE_BIWEEKLY_LINK` | Stripe link for the two-week plan |
| `CURRENCY_CODE` | `USD` |
| `MONTHLY_PRICE` | `230` |
| `BIWEEKLY_PRICE` | `140` |
| `DATABASE_PATH` | `/data/subscriptions.db` |

6. Click **Deploy** — Railway auto-builds and starts the bot 🎉

> Railway auto-redeploys on every GitHub push.

---

## 🔄 Subscription Flow

```
👤 User presses /start
        │
        ▼
📋 Selects a plan (Monthly $230 · Two-Week $140)
        │
        ▼
💳 Clicks "Pay Now" → redirected to Stripe checkout
        │
        ▼
✅ Completes payment → clicks "I've Paid" in the bot
        │
        ▼
🔔 Admin receives notification with Confirm / Reject buttons
        │
        ▼
🔗 Admin confirms → invite link sent to user automatically
        │
        ▼
⏰ Subscription expires → user removed from group automatically
```

---

## 🛡️ Bot Permissions Required

The bot **must be an admin** in your Telegram group with the following permissions:

- ✅ Invite users via link
- ✅ Ban users

---

## 📁 Project Structure

```
├── bot.py              # Main bot logic & handlers
├── config.py           # Environment variable loader
├── database.py         # SQLite database layer
├── requirements.txt    # Python dependencies
├── Procfile            # Railway start command
├── runtime.txt         # Python version pin
├── .env.example        # Environment variable template
└── .gitignore          # Git ignore rules
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from @BotFather |
| `TELEGRAM_GROUP_ID` | ✅ | Target group ID (negative number) |
| `ADMIN_USER_ID` | ✅ | Your Telegram user ID |
| `STRIPE_MONTHLY_LINK` | ✅ | Stripe payment link for monthly plan |
| `STRIPE_BIWEEKLY_LINK` | ✅ | Stripe payment link for two-week plan |
| `CURRENCY_CODE` | ✅ | Currency code (e.g. `USD`) |
| `MONTHLY_PRICE` | ✅ | Monthly plan price (display only) |
| `BIWEEKLY_PRICE` | ✅ | Two-week plan price (display only) |
| `DATABASE_PATH` | ✅ | Path to SQLite database file |

---

## 📄 License

MIT License — feel free to use and modify.
