import os
import asyncio
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# ================= CONFIG =================

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

bot = Bot(token=BOT_TOKEN)

# ================= HYPE LOGIC =================

def get_hype(keyword):
    url = f"https://nitter.net/search?q={keyword}&f=tweets"

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)

        if r.status_code != 200:
            return 0, 0, 0

        soup = BeautifulSoup(r.text, "html.parser")
        tweets = soup.select(".timeline-item")

        users = set()
        for t in tweets:
            user = t.select_one(".username")
            if user:
                users.add(user.text.strip())

        tweet_count = len(tweets)
        user_count = len(users)

        hype_score = (tweet_count * 1.5) + (user_count * 4)

        return tweet_count, user_count, round(hype_score, 2)

    except Exception:
        return 0, 0, 0

# ================= RUG RISK (REAL DATA) =================

def get_rug_risk(token_name):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={token_name}"
        r = requests.get(url, timeout=15)

        if r.status_code != 200:
            return "UNKNOWN ⚪", "DEX Screener unavailable"

        data = r.json()
        pairs = data.get("pairs", [])

        if not pairs:
            return "HIGH 🚨", "No DEX pair found"

        pair = pairs[0]

        liquidity = pair.get("liquidity", {}).get("usd", 0)
        fdv = pair.get("fdv", 0)
        age_minutes = pair.get("pairAge", 0)

        risk = 0
        reasons = []

        if liquidity < 20000:
            risk += 2
            reasons.append("Low liquidity")

        if fdv and liquidity / fdv < 0.05:
            risk += 1
            reasons.append("High FDV vs liquidity")

        if age_minutes < 60:
            risk += 1
            reasons.append("Very new pair")

        if risk >= 3:
            return "HIGH 🚨", ", ".join(reasons)
        elif risk == 2:
            return "MEDIUM ⚠️", ", ".join(reasons)
        else:
            return "LOW 🟢", "Liquidity looks reasonable"

    except Exception:
        return "UNKNOWN ⚪", "Rug check failed"

# ================= RUG INTERPRETATION =================

def explain_rug_risk(risk_level):
    if "LOW" in risk_level:
        meaning = "Token has reasonable liquidity and is tradable. Not an instant scam."
        action = "Small entry possible. Take partial profits early."

    elif "MEDIUM" in risk_level:
        meaning = "Liquidity is fragile. High volatility and whale risk."
        action = "Watch or scalp only. Do NOT hold."

    elif "HIGH" in risk_level:
        meaning = "Strong rug indicators detected."
        action = "Avoid completely. Do NOT buy."

    else:
        meaning = "Insufficient data. Token is too new or untracked."
        action = "Wait and recheck later."

    return meaning, action

# ================= TELEGRAM =================

async def send_alert(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception:
        pass

# ================= MAIN LOOP =================

async def run_bot():
    await asyncio.sleep(30)  # startup delay

    print("🤖 Memecoin bot running 24/7")

    while True:
        for keyword in KEYWORDS:
            tweets, users, score = get_hype(keyword)

            if score > 40 and users > 10:
                rug_level, rug_reason = get_rug_risk(keyword)
                meaning, action = explain_rug_risk(rug_level)

                alert = (
                    "🚨 MEMECOIN HYPE ALERT 🚨\n\n"
                    f"Keyword: {keyword}\n"
                    f"Tweets: {tweets}\n"
                    f"Unique Users: {users}\n"
                    f"Hype Score: {score}\n\n"
                    f"🛡 Rug Risk: {rug_level}\n"
                    f"Reason: {rug_reason}\n\n"
                    f"📘 What this means:\n{meaning}\n\n"
                    f"🎯 Suggested Action:\n{action}\n\n"
                    "⚠️ Probabilistic signal, not financial advice."
                )

                await send_alert(alert)

            time.sleep(10)  # slow down requests

        await asyncio.sleep(600)  # 10 min cooldown

# ================= ENTRY =================

if __name__ == "__main__":
    asyncio.run(run_bot())
