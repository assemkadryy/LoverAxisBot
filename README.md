🚀 Lover Axis Capital Bot

A Telegram subscription bot that automates paid access to private Telegram groups using Ziina payment integration.

⸻

📌 Overview

Lover Axis Capital Bot allows users to subscribe to premium Telegram groups through secure payment links. Once payment is confirmed, users receive an invite link to join the private group. When the subscription expires, users are automatically removed.

⸻

✨ Features
	•	💳 Payment integration with Ziina
	•	🔐 Private Telegram group access
	•	📅 Subscription plans (Monthly / 2 Weeks)
	•	🔗 Auto-generated invite links
	•	⏳ Automatic subscription expiration handling
	•	🚫 Auto removal of expired users
	•	⚡ Lightweight and scalable

⸻

🛠️ Tech Stack
	•	Python (aiogram)
	•	SQLite (database)
	•	Aiohttp (webhook handling)
	•	Railway (deployment)

⸻

⚙️ Setup Instructions

1. Clone the repository

git clone https://github.com/yourusername/lover-axis-bot.git
cd lover-axis-bot

2. Install dependencies

pip install -r requirements.txt

3. Configure environment variables

Create a .env file or set variables:

BOT_TOKEN=your_telegram_bot_token
GROUP_ID=your_private_group_id

4. Run the bot

python bot.py


⸻

🔗 Ziina Integration
	1.	Create payment links on Ziina dashboard
	2.	Set webhook URL:

https://your-app.railway.app/webhook

	3.	Ensure payment metadata includes user_id

⸻

🤖 Bot Flow
	1.	User sends /start
	2.	Bot shows subscription plans
	3.	User clicks payment link
	4.	Payment completed via Ziina
	5.	Webhook triggers bot
	6.	Bot sends private invite link
	7.	Subscription is stored
	8.	User removed after expiration

⸻

📂 Project Structure

bot.py
requirements.txt
db.sqlite


⸻

🚀 Deployment (Railway)
	1.	Push project to GitHub
	2.	Go to https://railway.app
	3.	Create new project → Deploy from GitHub
	4.	Add environment variables
	5.	Deploy

⸻

🔒 Security Notes
	•	Never expose your BOT_TOKEN
	•	Validate all webhook requests
	•	Do not trust client-side payment confirmation

⸻

📈 Future Improvements
	•	Admin dashboard
	•	Multi-language support
	•	Analytics & reporting
	•	Payment verification enhancements

⸻

📄 License

This project is for educational and commercial use.

⸻

🤝 Support

For setup help or customization, feel free to reach out.

⸻

💡 Built for premium communities, trading groups, and subscription-based services.
