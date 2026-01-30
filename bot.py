import asyncio
import time
import requests
from bs4 import BeautifulSoup
import os
from telegram import Bot

# ===== YOUR CREDENTIALS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")
CHAT_ID = "1252809476"
# ============================

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

bot = Bot(token=BOT_TOKEN)

def get_hype(keyword):
    url = f"https://nitter.net/search?q={keyword}&f=tweets"
    r = requests.get(url, headers=HEADERS, timeout=10)

    soup = BeautifulSoup(r.text, "html.parser")
    tweets = soup.select(".timeline-item")

    users = set()
    for t in tweets:
        user = t.select_one(".username")
        if user:
            users.add(user.text.strip())

    tweet_count = len(tweets)
    user_count = len(users)
    hype_score = (tweet_count * 2) + (user_count * 3)

    return tweet_count, user_count, hype_score

async def send_alert(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)

async def run_bot():
    while True:
        for kw in KEYWORDS:
            try:
                tweets, users, score = get_hype(kw)

                if score > 40 and users > 10:
                    message = (
                        "🚨 MEMECOIN HYPE ALERT 🚨\n\n"
                        f"Keyword: {kw}\n"
                        f"Tweets: {tweets}\n"
                        f"Users: {users}\n"
                        f"Hype Score: {score}\n\n"
                        "⚠️ Early-stage hype detected\n"
                        "DYOR – High risk"
                    )
                    await send_alert(message)

                time.sleep(5)  # anti-block

            except Exception as e:
                print("Error:", e)

        await asyncio.sleep(600)  # wait 10 minutes

if __name__ == "__main__":
    asyncio.run(run_bot())
