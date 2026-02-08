import telebot
import requests
import os

# --- НАСТРОЙКИ (Берем из секретов GitHub) ---
# os.getenv вытащит данные, которые ты укажешь в Settings -> Secrets
TOKEN = os.getenv("TG_TOKEN") 
GEMINI_KEY = os.getenv("GEMINI_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(TOKEN)

def get_ai_code(user_prompt):
    payload = {
        "contents": [{
            "parts": [{"text": f"Write only pure Python code. No explanations. Task: {user_prompt}"}]
        }]
    }
    try:
        response = requests.post(URL, json=payload, timeout=30)
        data = response.json()
        
        # Проверка на ошибки в ответе
        if 'candidates' not in data:
            return f"Ошибка ИИ: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"
            
        code = data['candidates'][0]['content']['parts'][0]['text']
        # Очистка от лишних знаков
        return code.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        return f"Ошибка при запросе: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🤖 Привет! Я твой ИИ-кодер на GitHub Actions.\nНапиши мне задачу, и я пришлю тебе готовый .py файл!")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    # Уведомление пользователя
    status_msg = bot.reply_to(message, "🧠 Генерирую код...")
    
    code = get_ai_code(message.text)
    
    if code.startswith("Ошибка"):
        bot.edit_message_text(code, message.chat.id, status_msg.message_id)
    else:
        # Временно создаем файл
        filename = "ai_solution.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Отправляем файл
        with open(filename, "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Код готов! Скачай и запусти его.")
        
        # Удаляем временный файл и лишнее сообщение
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
  
