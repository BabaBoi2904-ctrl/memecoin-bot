import os
import asyncio
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# ================= CONFIG =================

# Read token from Railway environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "1252809476"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

KEYWORDS = [
    "memecoin",
    "fair launch",
    "stealth launch",
    "new token",
    "$PEPE",
    "$FLOKI"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================================

bot = Bot(token=BOT_TOKEN)

# ================= FUNCTIONS =================

def get_hype(keyword):
    """
    Safely fetch hype data from Nitter.
    Never crashes the app.
    """
    url = f"https://nitter.net/search?q={keyword}&f=tweets"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        if response.status_code != 200:
            print(f"[WARN] Nitter blocked request for: {keyword}")
            return 0, 0, 0

        soup = BeautifulSoup(response.text, "html.parser")
        tweets = soup.select(".timeline-item")

        users = set()
        for tweet in tweets:
            user = tweet.select_one(".username")
            if user:
                users.add(user.text.strip())

        tweet_count = len(tweets)
        user_count = len(users)

        hype_score = (tweet_count * 1.5) + (user_count * 4)

        return tweet_count, user_count, round(hype_score, 2)

    except Exception as e:
        print(f"[ERROR] Fetch failed for {keyword}: {e}")
        return 0, 0, 0


async def send_alert(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")


# ================= MAIN LOOP =================

async def run_bot():
    # Give Railway time to settle before scraping
    await asyncio.sleep(30)

    print("🤖 Memecoin bot started and running 24/7")

    while True:
        for keyword in KEYWORDS:
            tweets, users, score = get_hype(keyword)

            if score > 40 and users > 10:
                alert_message = (
                    "🚨 MEMECOIN HYPE ALERT 🚨\n\n"
                    f"Keyword: {keyword}\n"
                    f"Tweets: {tweets}\n"
                    f"Unique Users: {users}\n"
                    f"Hype Score: {score}\n\n"
                    "⚠️ Early-stage hype detected\n"
                    "DYOR – High risk"
                )
                await send_alert(alert_message)

            # Slow down between keywords (avoid blocks)
            time.sleep(10)

        # Wait before next full scan
        await asyncio.sleep(600)  # 10 minutes


# ================= ENTRY POINT =================

if __name__ == "__main__":
    asyncio.run(run_bot())
