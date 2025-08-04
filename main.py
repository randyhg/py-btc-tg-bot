import asyncio
import requests
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import random

# --- CONFIG ---
BOT_TOKEN = '8070451174:AAEwthb5DIY5nhm3GJM16OJGrMGwWaQuQTI'
CHAT_ID = '-4789081490'
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

# Message handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🤖 Welcome to the BTC Price Bot!

Commands available:
/start - Show this welcome message
/price - Get current BTC price
/help - Show help information
/status - Check bot status

The bot automatically sends BTC price updates when the price changes by $1000 or more.
    """
    await update.message.reply_text(welcome_message)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    price = get_btc_price()
    if isinstance(price, (float, int)):
        emoji = "💰"
        message = f"{emoji} Current BTC Price: ${price:,.2f}"
    else:
        message = f"❌ {price}"
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
📚 BTC Price Bot Help

This bot monitors Bitcoin price and sends notifications when the price changes significantly.

Features:
• Automatic price monitoring every 8-13 seconds
• Notifications when price changes by $1000 or more
• Manual price checking with /price command
• Price trend indicators (📈📉)

Commands:
/start - Welcome message
/price - Get current BTC price
/help - This help message
/status - Bot status

Data source: Binance API
    """
    await update.message.reply_text(help_message)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    last_group = read_last_price_group()
    if last_group is not None:
        status_message = f"✅ Bot is running\n📊 Last price group: ${last_group},000-${last_group+1},000"
    else:
        status_message = "✅ Bot is running\n📊 No previous price data"
    await update.message.reply_text(status_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return
    # """Handle all other messages"""
    # message_type = update.message.chat.type
    # text = update.message.text
    
    # print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    
    # # Respond to common questions
    # if 'hello' in text.lower() or 'hi' in text.lower():
    #     await update.message.reply_text('Hello! 👋 Use /help to see available commands.')
    # elif 'btc' in text.lower() or 'bitcoin' in text.lower():
    #     await price_command(update, context)
    # else:
    #     await update.message.reply_text('I\'m a BTC price bot! Use /help to see what I can do.')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f'Update {update} caused error {context.error}')

async def send_btc_price():
    while True:
        try:
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
                print(price)

            await asyncio.sleep(random.choice(RANDOM_DELAY_LIST))
        except Exception as e:
            print(f"Error in price monitoring: {e}")
            await asyncio.sleep(10)

async def btc_price_job(context: ContextTypes.DEFAULT_TYPE):
    await send_btc_price()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('price', price_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status_command))

    # Fallback for other text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(
        btc_price_job,
        interval=10,   
        first=10        
    )

    print('Starting bot...')
    app.run_polling(poll_interval=1.0)

if __name__ == "__main__":
    main()