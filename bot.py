import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "Доступные команды:\n"
        "/show_city <город> — показать город на карте (на английском)\n"
        "/remember_city <город> — сохранить город в свой список\n"
        "/show_my_cities — показать все сохранённые города на карте"
    )

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи название города. Пример: /show_city London")
        return

    city_name = parts[-1]
    coordinates = manager.get_coordinates(city_name)

    if not coordinates:
        bot.send_message(message.chat.id, f'Город «{city_name}» не найден. Убедись, что он написан на английском!')
        return

    bot.send_message(message.chat.id, f'Строю карту для города {city_name}...')
    buf = manager.create_graph([city_name])
    bot.send_photo(message.chat.id, buf)

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи название города. Пример: /remember_city London")
        return

    user_id = message.chat.id
    city_name = parts[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранён!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if not cities:
        bot.send_message(message.chat.id, 'У тебя пока нет сохранённых городов. Используй /remember_city, чтобы добавить.')
        return

    city_list = ', '.join(cities)
    bot.send_message(message.chat.id, f'Твои города: {city_list}\nСтрою карту...')
    buf = manager.create_graph(cities)
    bot.send_photo(message.chat.id, buf)

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
