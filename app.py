import os
import threading
import time
from flask import Flask
from bot_simple import main as bot_main

app = Flask(__name__)

def run_bot():
    while True:
        try:
            bot_main()
        except Exception as e:
            print(f"Ошибка бота: {e}")
            time.sleep(10)

@app.route('/')
def home():
    return "🤖 VK Ферма Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
