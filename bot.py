import telebot
import requests
import os

# Получаем ключи из окружения (их передаст Workflow)
TOKEN = os.getenv("TG_TOKEN") 
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

bot = telebot.TeleBot(TOKEN)

def get_ai_code(user_prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Write only pure Python code. No explanations. Use utf-8."},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        if 'choices' in data:
            code = data['choices'][0]['message']['content']
            return code.replace("```python", "").replace("```", "").strip()
        return f"Ошибка API: {data.get('error', {}).get('message', 'Unknown')}"
    except Exception as e:
        return f"Ошибка запроса: {e}"

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    status = bot.reply_to(message, "⏳ Генерирую файл...")
    code = get_ai_code(message.text)
    
    if code.startswith("Ошибка"):
        bot.edit_message_text(code, message.chat.id, status.message_id)
    else:
        with open("solution.py", "w", encoding="utf-8") as f:
            f.write(code)
        with open("solution.py", "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Готово")
        bot.delete_message(message.chat.id, status.message_id)

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()
