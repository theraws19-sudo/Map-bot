import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """Доступные команды:
/start - Начать работу с ботом
/help - Показать список команд
/show_city [название] - Показать город на карте (например: /show_city Tokyo)
/remember_city [название] - Запомнить город (например: /remember_city Moscow)
/show_my_cities - Показать все сохраненные города на карте
/my_cities_list - Список всех сохраненных городов
/distance [город1] [город2] - Показать расстояние между городами

⚠️ Названия городов должны быть на английском языке!"""
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        city_name = message.text.split(maxsplit=1)[1]
        
        # Проверяем, существует ли город в базе
        coordinates = manager.get_coordinates(city_name)
        if not coordinates:
            bot.send_message(message.chat.id, 
                           f'Город {city_name} не найден в базе данных. Убедитесь, что название написано на английском!')
            return
        
        # Создаем карту с одним городом
        path = f'city_{city_name}.png'
        manager.create_graph(path, [city_name])
        
        # Отправляем карту пользователю
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, 
                          caption=f'📍 Город {city_name} на карте')
        
        # Удаляем временный файл
        import os
        os.remove(path)
        
    except IndexError:
        bot.send_message(message.chat.id, 
                        'Пожалуйста, укажите название города. Например: /show_city Tokyo')


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    try:
        user_id = message.chat.id
        city_name = message.text.split(maxsplit=1)[1]
        
        if manager.add_city(user_id, city_name):
            bot.send_message(message.chat.id, 
                           f'✅ Город {city_name} успешно сохранен!')
        else:
            bot.send_message(message.chat.id, 
                           f'❌ Город {city_name} не найден в базе данных. Убедитесь, что название написано на английском!')
    except IndexError:
        bot.send_message(message.chat.id, 
                        'Пожалуйста, укажите название города. Например: /remember_city Tokyo')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    
    if not cities:
        bot.send_message(message.chat.id, 
                        'У вас пока нет сохраненных городов. Используйте /remember_city [название] для добавления.')
        return
    
    # Создаем карту со всеми городами пользователя
    path = f'user_{message.chat.id}_cities.png'
    manager.create_graph(path, cities)
    
    # Отправляем карту
    with open(path, 'rb') as photo:
        cities_list = ', '.join(cities)
        bot.send_photo(message.chat.id, photo, 
                      caption=f'🗺️ Ваши города ({len(cities)}): {cities_list}')
    
    # Удаляем временный файл
    import os
    os.remove(path)


@bot.message_handler(commands=['my_cities_list'])
def handle_cities_list(message):
    """Показывает список сохраненных городов без карты"""
    cities = manager.select_cities(message.chat.id)
    
    if not cities:
        bot.send_message(message.chat.id, 
                        'У вас пока нет сохраненных городов.')
        return
    
    cities_text = '\n'.join([f'{i+1}. {city}' for i, city in enumerate(cities)])
    bot.send_message(message.chat.id, 
                    f'📋 Ваши сохраненные города ({len(cities)}):\n\n{cities_text}')


@bot.message_handler(commands=['distance'])
def handle_distance(message):
    """Показывает расстояние между двумя городами"""
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, 
                           'Пожалуйста, укажите два города. Например: /distance Tokyo Moscow')
            return
        
        city1 = parts[1]
        city2 = parts[2]
        
        result = manager.draw_distance(city1, city2)
        
        if result is None:
            bot.send_message(message.chat.id, 
                           'Один или оба города не найдены в базе данных.')
            return
        
        path, distance = result
        
        # Отправляем карту с расстоянием
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, 
                          caption=f'📏 Расстояние между {city1} и {city2}: {distance:.0f} км')
        
        # Удаляем временный файл
        import os
        os.remove(path)
        
    except Exception as e:
        bot.send_message(message.chat.id, 
                        f'Произошла ошибка: {str(e)}')


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()