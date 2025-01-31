import requests
import datetime
import logging

# Configuration
API_ENDPOINTS = {
    "coingecko": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=artificial-intelligence&order=market_cap_desc",
    "pumpfun": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=pump-fun&order=market_cap_desc",
}
MARKET_CAP_THRESHOLD = 1000000
FIBONACCI_LEVEL = 1
SECONDARY_PUMP_THRESHOLD = 1.3
RECENT_DURATION_DAYS = 90

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7204923924:AAFoD8stUUZ8fehzEyDWyDB47M3siNhbyFI"  # Replace with your bot token
TELEGRAM_CHAT_ID = "1069328752"  # Replace with your chat ID

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_telegram_message(message):
    """Send a message via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        logger.exception("Error sending Telegram message")

def fetch_data():
    """Fetch data from the APIs or websites."""
    data = []
    for name, endpoint in API_ENDPOINTS.items():
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data.extend(response.json())  # Extend the list with the fetched data
            else:
                logger.error(f"Failed to fetch data from {name}: {response.status_code}")
        except Exception as e:
            logger.exception(f"Error fetching data from {name}")
    return data

def filter_coins(data):
    """Filter coins based on the criteria."""
    filtered_coins = []
    now = datetime.datetime.now()
    for coin in data:
        try:
            # Check market cap
            market_cap = coin.get('market_cap', 0)
            if market_cap < MARKET_CAP_THRESHOLD:
                continue

            # Check listing date
            listing_date_str = coin.get('genesis_date')
            if listing_date_str:
                listing_date = datetime.datetime.strptime(listing_date_str, '%Y-%m-%d')
                if (now - listing_date).days > RECENT_DURATION_DAYS:
                    continue

            # Check price retracement and secondary pump
            ath = coin.get('ath', 0)
            current_price = coin.get('current_price', 0)
            fib_price = ath * (1 - FIBONACCI_LEVEL)
            if current_price < fib_price:
                continue

            # Check secondary pump
            price_change_24h = coin.get('price_change_percentage_24h', 0)
            if price_change_24h < (SECONDARY_PUMP_THRESHOLD - 1) * 100:
                continue

            filtered_coins.append(coin)
        except Exception as e:
            logger.exception(f"Error processing coin: {coin.get('name', 'Unknown')}")
    return filtered_coins

def main():
    data = fetch_data()
    filtered_coins = filter_coins(data)
    if filtered_coins:
        message = "Filtered Coins:\n"
        for coin in filtered_coins:
            coin_info = f"{coin['name']} ({coin['symbol']}) - Market Cap: ${coin['market_cap']:,} - Current Price: ${coin['current_price']}- 24H price change: %{coin['price_change_percentage_24h']:,}"
            logger.info(coin_info)
            message += coin_info + "\n"
        send_telegram_message(message)
    else:
        logger.info("No coins matched the criteria.")
        send_telegram_message("No coins matched the criteria.")


if __name__ == "__main__":
    main()
