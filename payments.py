import aiohttp
from config import ZIINA_API_BASE, ZIINA_API_TOKEN, ZIINA_TEST_MODE


async def create_payment_intent(amount: int, currency: str,
                                message: str) -> dict:
    """Create a Ziina payment intent.

    Args:
        amount: Amount in main currency unit (e.g. 200 for 200 AED).
        currency: ISO-4217 currency code.
        message: Description shown on payment page.

    Returns:
        Dict with 'id' and 'redirect_url' keys.
    """
    amount_fils = amount * 100  # convert to smallest currency unit

    payload = {
        "amount": amount_fils,
        "currency_code": currency,
        "message": message,
        "test": ZIINA_TEST_MODE,
    }

    headers = {
        "Authorization": f"Bearer {ZIINA_API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ZIINA_API_BASE}/payment_intent",
            json=payload,
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return {
                "id": data["id"],
                "redirect_url": data["redirect_url"],
            }


async def get_payment_status(payment_intent_id: str) -> str:
    """Check the status of a payment intent.

    Returns one of: requires_payment_instrument, requires_user_action,
    pending, completed, failed, canceled.
    """
    headers = {
        "Authorization": f"Bearer {ZIINA_API_TOKEN}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ZIINA_API_BASE}/payment_intent/{payment_intent_id}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["status"]
