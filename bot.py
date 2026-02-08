import telebot
import requests
import os

# Берем ключи из секретов GitHub (env переменные)
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
            {
                "role": "system", 
                "content": "You are a professional Python coder. Write only pure code without explanations. Use utf-8 encoding."
            },
            {
                "role": "user", 
                "content": f"Write Python code for: {user_prompt}"
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if 'choices' in data:
            raw_code = data['choices'][0]['message']['content']
            # Очистка от маркдаун-разметки типа ```python ... ```
            clean_code = raw_code.replace("```python", "").replace("```", "").strip()
            return clean_code
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown API Error')
            return f"Error from DeepSeek: {error_msg}"
            
    except Exception as e:
        return f"Request Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Опиши задачу, и я пришлю тебе готовый .py файл с кодом от DeepSeek.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    status_msg = bot.reply_to(message, "🚀 DeepSeek генерирует код, подожди...")
    
    code_result = get_ai_code(message.text)
    
    if code_result.startswith("Error"):
        bot.edit_message_text(code_result, message.chat.id, status_msg.message_id)
    else:
        # Сохраняем код во временный файл
        filename = "generated_code.py"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code_result)
            
            # Отправляем файл пользователю
            with open(filename, "rb") as f:
                bot.send_document(
                    message.chat.id, 
                    f, 
                    caption="✅ Твой код готов! Создано нейросетью DeepSeek."
                )
            
            # Удаляем файл после отправки и убираем статус-сообщение
            os.remove(filename)
            bot.delete_message(message.chat.id, status_msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"Ошибка при создании файла: {e}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
