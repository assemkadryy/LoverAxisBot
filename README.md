# بوت الاشتراكات - Telegram Subscription Bot

بوت تيليجرام لإدارة اشتراكات المجموعة المميزة مع بوابة دفع Stripe.

---

## المميزات

- اشتراك شهري (30 يوم) واشتراك أسبوعين (14 يوم)
- دفع آمن عبر Stripe
- إرسال رابط دخول المجموعة تلقائياً بعد تأكيد الدفع
- إزالة الأعضاء تلقائياً عند انتهاء الاشتراك
- لوحة تحكم للمشرف لتأكيد أو رفض طلبات الاشتراك
- عرض حالة الاشتراك للمستخدم

---

## المتطلبات

- Python 3.11+
- حساب Telegram Bot (من @BotFather)
- حساب Stripe
- حساب Railway (للنشر)

---

## الإعداد المحلي

### 1. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 2. إعداد ملف البيئة

```bash
cp .env.example .env
```

ثم عدّل ملف `.env` بالقيم الخاصة بك:

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

### 3. تشغيل البوت

```bash
python3 bot.py
```

---

## النشر على Railway

1. ارفع الملفات على GitHub
2. اذهب إلى [railway.app](https://railway.app) وسجّل دخولك بحساب GitHub
3. اختر **New Project → Deploy from GitHub Repo**
4. أضف **Volume** بمسار `/data`
5. أضف متغيرات البيئة في تبويب **Variables**:

| المتغير | القيمة |
|---------|--------|
| `TELEGRAM_BOT_TOKEN` | توكن البوت من BotFather |
| `TELEGRAM_GROUP_ID` | ID المجموعة |
| `ADMIN_USER_ID` | ID حسابك على تيليجرام |
| `STRIPE_MONTHLY_LINK` | رابط Stripe للاشتراك الشهري |
| `STRIPE_BIWEEKLY_LINK` | رابط Stripe لاشتراك الأسبوعين |
| `CURRENCY_CODE` | `USD` |
| `MONTHLY_PRICE` | `230` |
| `BIWEEKLY_PRICE` | `140` |
| `DATABASE_PATH` | `/data/subscriptions.db` |

6. اضغط **Deploy**

---

## كيفية عمل البوت

```
المستخدم يضغط /start
        ↓
يختار الباقة (شهري أو أسبوعين)
        ↓
يضغط "ادفع الآن" → ينتقل إلى صفحة Stripe
        ↓
يكمل الدفع ويضغط "دفعت"
        ↓
يصل إشعار للمشرف مع زر تأكيد أو رفض
        ↓
المشرف يضغط تأكيد → يصل رابط الدخول للمستخدم تلقائياً
        ↓
عند انتهاء الاشتراك → يتم إزالة العضو تلقائياً
```

---

## صلاحيات البوت في المجموعة

يجب أن يكون البوت مشرفاً في المجموعة مع تفعيل:
- **دعوة المستخدمين عبر روابط**
- **حظر المستخدمين**

---

## الملفات

| الملف | الوظيفة |
|-------|---------|
| `bot.py` | الكود الرئيسي للبوت |
| `config.py` | إعدادات متغيرات البيئة |
| `database.py` | قاعدة بيانات SQLite |
| `requirements.txt` | مكتبات Python |
| `Procfile` | أمر تشغيل Railway |
| `runtime.txt` | إصدار Python |
