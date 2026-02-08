import telebot
import requests
import os

# Берем ключи из секретов GitHub
TOKEN = os.getenv("TG_TOKEN") 
GEMINI_KEY = os.getenv("GEMINI_KEY")

bot = telebot.TeleBot(TOKEN)

def get_ai_code(user_prompt):
    # Используем модель Gemini 3 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Write only pure Python code. No explanations. Task: {user_prompt}"}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        # Парсим ответ от Gemini 3
        if 'candidates' in data:
            raw_code = data['candidates'][0]['content']['parts'][0]['text']
            # Убираем лишний мусор, если модель его добавила
            clean_code = raw_code.replace("```python", "").replace("```", "").strip()
            return clean_code
        else:
            return f"Ошибка Gemini: {data.get('error', {}).get('message', 'Нет ответа от модели')}"
    except Exception as e:
        return f"Ошибка сети: {str(e)}"

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    status_msg = bot.reply_to(message, "⚡ Gemini 3 Flash генерирует код...")
    code = get_ai_code(message.text)
    
    if code.startswith("Ошибка"):
        bot.edit_message_text(code, message.chat.id, status_msg.message_id)
    else:
        filename = "solution.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        
        with open(filename, "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Готово! Сделано на Gemini 3 Flash")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
