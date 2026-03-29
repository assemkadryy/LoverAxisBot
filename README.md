# 🤖 Telegram Subscription Bot

> A production-ready Telegram bot for managing premium group subscriptions with fully automated Stripe payment processing, invite link generation, and subscription lifecycle management.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💳 **Stripe API Integration** | Dynamic checkout sessions created per user via Stripe API |
| 🔐 **Secure Payments** | Each user gets a unique payment link tied to their Telegram ID |
| 📦 **Product Catalog Linked** | Every transaction is linked to your Stripe product catalog |
| 📅 **Flexible Plans** | Monthly (30 days) and two-week (14 days) subscriptions |
| ⚡ **Fully Automatic** | Invite link sent instantly after payment — zero manual work |
| 🔗 **Single-Use Invite Links** | Group invite links expire after 24 hours and one use |
| ⏰ **Auto Expiry** | Members removed automatically when subscription ends |
| 📌 **Status Check** | Users can view their active subscription anytime |
| 🔄 **Renewal Support** | Easy subscription renewal flow |
| 🛡️ **Webhook Verification** | Every Stripe event is cryptographically verified |

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Bot Framework:** [python-telegram-bot](https://github.com/python-tg/python-telegram-bot) v21
- **Web Server:** aiohttp (for Stripe webhooks)
- **Database:** SQLite via `aiosqlite`
- **Payments:** Stripe API (dynamic checkout sessions + product catalog)
- **Hosting:** Railway
- **Scheduler:** APScheduler

---

## 💳 Payment Flow

```
👤 User presses /start
        │
        ▼
📋 Selects a plan (Monthly $230 · Two-Week $140)
        │
        ▼
🔗 Bot creates a unique Stripe checkout session via API
   (linked to Stripe product catalog)
        │
        ▼
💳 User pays on Stripe (unique link per user)
        │
        ▼
⚡ Stripe fires webhook → Bot verifies signature
        │
        ▼
🔗 Invite link generated & sent to user automatically
        │
        ▼
⏰ Subscription expires → User removed from group automatically
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot token — from [@BotFather](https://t.me/BotFather)
- Stripe account with API access and products created
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

Edit `.env` with your values (see Environment Variables section below).

### 3️⃣ Run

```bash
python3 bot.py
```

---

## ☁️ Deploy on Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub Repo**
3. Add a **Volume** → mount path: `/data`
4. Go to **Settings → Networking → Generate Domain** → set port to `8080`
5. Add all environment variables under the **Variables** tab
6. Click **Deploy** 🎉

> Railway auto-redeploys on every GitHub push.

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_GROUP_ID` | Your Telegram group ID (negative number) |
| `ADMIN_USER_ID` | Your personal Telegram user ID |
| `TELEGRAM_BOT_USERNAME` | Bot username without @ (e.g. `LoverAxisBot`) |
| `STRIPE_SECRET_KEY` | Stripe secret API key (`sk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) |
| `MONTHLY_PRICE` | Monthly price for display (`230`) |
| `BIWEEKLY_PRICE` | Two-week price for display (`140`) |
| `CURRENCY_CODE` | Currency code (`USD`) |
| `PUBLIC_URL` | Your Railway public URL |
| `DATABASE_PATH` | `/data/subscriptions.db` |

---

## 🔗 Stripe Setup

### 1. Get API Keys
- Stripe Dashboard → **Developers → API keys**
- Copy the **Secret key** (`sk_live_...`) → add to Railway as `STRIPE_SECRET_KEY`

### 2. Create Products
- Stripe Dashboard → **Product catalog → + Add product**
- Create one product for each plan with the correct price
- Copy each **Price ID** (`price_...`) from the product page

### 3. Create Webhook
- Stripe Dashboard → **Developers → Webhooks → Add destination**
- Select **Your account** → choose latest API version
- Select event: `checkout.session.completed`
- Endpoint URL:
```
https://your-railway-url.up.railway.app/webhook/stripe
```
- After creation, **Reveal** signing secret (`whsec_...`) → add to Railway as `STRIPE_WEBHOOK_SECRET`

---

## 🛡️ Bot Permissions Required

The bot **must be an admin** in your Telegram group with:

- ✅ Invite users via link
- ✅ Ban users

---

## 📁 Project Structure

```
├── bot.py              # Main bot logic, webhook server & handlers
├── config.py           # Environment variable loader
├── database.py         # SQLite database layer
├── requirements.txt    # Python dependencies
├── Procfile            # Railway start command
├── runtime.txt         # Python version pin
├── .env.example        # Environment variable template
└── .gitignore          # Git ignore rules
```

---

## 📄 License

MIT License — feel free to use and modify.
