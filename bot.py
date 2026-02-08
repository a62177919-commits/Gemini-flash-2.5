import telebot
import requests
import os

# Получаем данные из секретов GitHub
TOKEN = os.getenv("TG_TOKEN") 
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Список моделей: сначала пробуем новейшую 2.0, затем 1.5
MODELS = ["gemini-2.0-flash", "gemini-1.5-flash"]

bot = telebot.TeleBot(TOKEN)

def get_ai_answer(prompt):
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        try:
            response = requests.post(url, json=payload, timeout=20)
            data = response.json()
            
            if 'candidates' in data:
                return data['candidates'][0]['content']['parts'][0]['text']
            # Если ошибка "not found", цикл пойдет к следующей модели
            continue 
        except Exception:
            continue
            
    return "❌ Ошибка: Модели Gemini 2.0 и 1.5 недоступны для этого ключа. Проверь регион в Google AI Studio."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Бот на базе Gemini 2.0 Flash запущен!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Отправляем статус "печатает", чтобы пользователь видел активность
    bot.send_chat_action(message.chat.id, 'typing')
    
    answer = get_ai_answer(message.text)
    
    # Если текст слишком длинный, Телеграм его не пропустит (лимит 4096 символов)
    if len(answer) > 4000:
        for x in range(0, len(answer), 4000):
            bot.send_message(message.chat.id, answer[x:x+4000])
    else:
        bot.reply_to(message, answer)

if __name__ == "__main__":
    print("Бот погнал...")
    bot.infinity_polling()
    
