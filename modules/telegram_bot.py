import os
import sys
import json
import logging
import asyncio
from telegram import Bot

try:
	# main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('telegram_bot', 'modules/logs/telegram_bot.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('telegram_bot', 'logs/telegram_bot.log')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# ALLOWED_USER_IDS: Virgülle ayrılmış kullanıcı ID'lerini integer listesine dönüştürür.
allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [int(uid.strip()) for uid in allowed_ids_str.split(",") if uid.strip().isdigit()]

# ALLOWED_CHAT_IDS: Virgülle ayrılmış chat (grup) ID'lerini integer listesine dönüştürür.
allowed_chats_str = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = [int(cid.strip()) for cid in allowed_chats_str.split(",") if cid.strip().isdigit()]


def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Dosya %s yüklenirken hata: %s", filename, e)
        return None

def split_message(text, chunk_size=4096):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

async def main_async(results_file):
    
    logger.info("Telegram bot is called")

    if not TELEGRAM_TOKEN:
        logger.warning("No Telegram Token is set, Bot is disabled")
        return

    if not ALLOWED_USER_IDS or ALLOWED_CHAT_IDS:
        logger.warning("No target chat id or user id is set, Bot is disabled")
        return

    if not os.path.exists(results_file):
        logger.error("Results file %s does not exist, Bot is disabled", results_file)
        return

    # Load results from the file
    results = load_json(results_file)
    if not results:
        logger.error("Failed to load results from %s", results_file)
        return

    # Convert results to a readable message
    message_text = json.dumps(results, indent=2, ensure_ascii=False)
    
    bot = Bot(token=TELEGRAM_TOKEN)
    chunks = split_message(message_text)
    
    for uid in ALLOWED_USER_IDS:
        for chunk in chunks:
            try:
                await bot.send_message(chat_id=uid, text=chunk)
                logger.info("Mesaj kullanıcı %s'ya gönderildi.", uid)
            except Exception as e:
                logger.error("Kullanıcı %s için mesaj gönderilemedi: %s", uid, e)
    
    for cid in ALLOWED_CHAT_IDS:
        for chunk in chunks:
            try:
                await bot.send_message(chat_id=cid, text=chunk)
                logger.info("Mesaj chat %s'ye gönderildi.", cid)
            except Exception as e:
                logger.error("Chat %s için mesaj gönderilemedi: %s", cid, e)
    
    logger.info("Results sent successfully by Telegram bot.")

def run_telegram_bot(results_file):
    asyncio.run(main_async(results_file))

if __name__ == "__main__":
    results_file_path = input("Enter path for json file to send: ")
    run_telegram_bot()