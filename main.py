import asyncio
import requests
from telegram import Bot
import os
import random

# --- CONFIG ---
BOT_TOKEN = '8070451174:AAEwthb5DIY5nhm3GJM16OJGrMGwWaQuQTI'
CHAT_ID = '-4789081490'  # You can use your own Telegram ID
PRICE_FILE = 'last_price.txt'
RANDOM_DELAY_LIST = [8,9,10,11,12,13]

bot = Bot(token=BOT_TOKEN)

def get_btc_price():
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    try:
        response = requests.get(url)
        data = response.json()
        price = float(data['price'])
        return price
    except Exception as e:
        return f"Error fetching BTC price: {e}"

def read_last_price():
    if not os.path.exists(PRICE_FILE):
        return None
    try:
        with open(PRICE_FILE, 'r') as f:
            content = f.read().strip()
            # Check if it's a price (contains decimal) or group (integer)
            if '.' in content:
                return float(content)
            else:
                return int(content)
    except Exception:
        return None


def read_last_price_group():
    if not os.path.exists(PRICE_FILE):
        return None
    try:
        with open(PRICE_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return None

def write_price_group(group):
    with open(PRICE_FILE, 'w') as f:
        f.write(str(group))

async def send_btc_price():
    while True:
        price = get_btc_price()

        if isinstance(price, float) or isinstance(price, int):
            price_group = int(price // 1000)  # E.g. 122,747 -> 122

            last_group = read_last_price_group()

            if last_group != price_group:
                if last_group is None:
                    emoji = "🤑"  # First time, use default emoji
                elif price_group > last_group:
                    emoji = "📈"  # Price increased - profit
                elif price_group < last_group:
                    emoji = "📉"  # Price decreased - loss
                else:
                    emoji = "➡️"  # Price unchanged 
                message = f"{emoji} It is: ${price:,.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=message)
                write_price_group(price_group)
        else:
            print(price)  # Error or failed fetch

        await asyncio.sleep(random.choice(RANDOM_DELAY_LIST))

if __name__ == "__main__":
    asyncio.run(send_btc_price())