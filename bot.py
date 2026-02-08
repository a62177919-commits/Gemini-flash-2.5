import telebot
import requests
import os

TOKEN = os.getenv("TG_TOKEN") 
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Самый стабильный адрес для обычных API ключей
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(TOKEN)

def get_ai_response(user_prompt):
    payload = {
        "contents": [{
            "parts": [{"text": user_prompt}]
        }]
    }
    try:
        response = requests.post(URL, json=payload, timeout=20)
        data = response.json()
        
        # Проверка на ошибки от самого Google
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = data.get('error', {}).get('message', 'Неизвестная ошибка API')
            return f"Ошибка от Google: {error_msg}"
    except Exception as e:
        return f"Ошибка соединения: {e}"

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    wait_msg = bot.reply_to(message, "⏳ Связываюсь с ИИ...")
    answer = get_ai_response(message.text)
    bot.edit_message_text(answer, message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()
    
