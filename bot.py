import telebot
import requests
import os

# Данные берутся из Secrets твоего репозитория
TOKEN = os.getenv("TG_TOKEN") 
GEMINI_KEY = os.getenv("GEMINI_KEY")
# Используем стабильную версию модели
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

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
        
        if 'candidates' not in data:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            return f"Ошибка ИИ: {error_msg}"
            
        code = data['candidates'][0]['content']['parts'][0]['text']
        return code.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        return f"Ошибка запроса: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 Бот запущен через GitHub Actions!\nПришли задачу, и я сгенерирую код.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    status_msg = bot.reply_to(message, "🤖 Думаю...")
    code = get_ai_code(message.text)
    
    if code.startswith("Ошибка"):
        bot.edit_message_text(code, message.chat.id, status_msg.message_id)
    else:
        filename = "solution.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        
        with open(filename, "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Готово!")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Бот в сети...")
    bot.infinity_polling()
    
