import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@название_канала"  # замените на ваш канал

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения очков и состояния
user_data = {}

# Вопросы и варианты
questions = [
    {
        "q": "1️⃣ Какое искусство тебе ближе всего?",
        "a": [
            ("📜 Поэзия", {"Mayakovsky": 2, "Tsvetaeva": 2, "Akhmatova": 2, "Pasternak": 2, "Brodsky": 2, "Esenin": 1}),
            ("🎻 Музыка", {"Esenin": 2, "Akhmatova": 1, "Brodsky": 1, "Pasternak": 1}),
            ("🎭 Театр", {"Mayakovsky": 1, "Tsvetaeva": 1, "Brodsky": 2}),
            ("🎨 Живопись", {"Akhmatova": 1, "Esenin": 1})
        ]
    }
    # Остальные вопросы можно добавить аналогично
]

@bot.message_handler(commands=["start"])
def start_quiz(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": 0, "scores": {}}
    ask_question(chat_id)

def ask_question(chat_id):
    step = user_data[chat_id]["step"]
    if step < len(questions):
        q = questions[step]
        markup = InlineKeyboardMarkup()
        for i, (text, scores) in enumerate(q["a"]):
            markup.add(InlineKeyboardButton(text, callback_data=f"ans_{step}_{i}"))
        bot.send_message(chat_id, q["q"], reply_markup=markup)
    else:
        check_subscription(chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ans_"))
def handle_answer(call):
    chat_id = call.message.chat.id
    _, step, index = call.data.split("_")
    step = int(step)
    index = int(index)
    scores = questions[step]["a"][index][1]
    for poet, pts in scores.items():
        user_data[chat_id]["scores"][poet] = user_data[chat_id]["scores"].get(poet, 0) + pts
    user_data[chat_id]["step"] += 1
    ask_question(chat_id)

def check_subscription(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
        if member.status in ['creator', 'administrator', 'member']:
            show_result(chat_id)
        else:
            ask_to_subscribe(chat_id)
    except Exception:
        ask_to_subscribe(chat_id)

def ask_to_subscribe(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_sub"))
    bot.send_message(chat_id, f"Пожалуйста, подпишись на канал {CHANNEL_USERNAME} и нажми кнопку ниже", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def handle_check_sub(call):
    check_subscription(call.message.chat.id)

def show_result(chat_id):
    scores = user_data[chat_id]["scores"]
    result = max(scores, key=scores.get)
    poet_names = {
        "Mayakovsky": "⚡ Ты — Владимир Маяковский!",
        "Tsvetaeva": "🕯 Ты — Марина Цветаева!",
        "Akhmatova": "📜 Ты — Анна Ахматова!",
        "Esenin": "🌿 Ты — Сергей Есенин!",
        "Pasternak": "🧠 Ты — Борис Пастернак!",
        "Brodsky": "🕶 Ты — Иосиф Бродский!"
    }
    bot.send_message(chat_id, poet_names.get(result, "Поэт не найден."))

bot.infinity_polling()