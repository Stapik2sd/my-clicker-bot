# events.py
import random
import time
from database import get_user, update_user

# Список возможных событий
WEATHER_EVENTS = {
    'солнечно': {
        'name': '☀️ Солнечная погода',
        'effect': 'bonus',
        'description': 'Солнце помогло урожаю!',
        'effect_value': 20,
        'chance': 30
    },
    'дождь': {
        'name': '🌧️ Дождливая погода',
        'effect': 'water',
        'description': 'Дождь полил твои растения!',
        'effect_value': 15,
        'chance': 25
    },
    'град': {
        'name': '🌨️ Град',
        'effect': 'damage',
        'description': 'Град повредил урожай!',
        'effect_value': -15,
        'chance': 10
    },
    'ветер': {
        'name': '💨 Сильный ветер',
        'effect': 'steal',
        'description': 'Ветер унёс часть урожая!',
        'effect_value': -10,
        'chance': 15
    },
    'радуга': {
        'name': '🌈 Радуга',
        'effect': 'luck',
        'description': 'Радуга принесла удачу!',
        'effect_value': 50,
        'chance': 5
    },
    'туман': {
        'name': '🌫️ Туман',
        'effect': 'mystery',
        'description': 'В тумане ты нашёл сокровище!',
        'effect_value': 30,
        'chance': 10
    },
    'жара': {
        'name': '🔥 Аномальная жара',
        'effect': 'damage',
        'description': 'Жара засушила растения!',
        'effect_value': -20,
        'chance': 8
    },
    'ураган': {
        'name': '🌀 Ураган',
        'effect': 'disaster',
        'description': 'Ураган разрушил часть фермы!',
        'effect_value': -50,
        'chance': 2
    }
}

# Случайные события (не связанные с погодой)
RANDOM_EVENTS = {
    'клад': {
        'name': '💰 Нашёл клад!',
        'description': 'Ты нашёл старинный клад на поле!',
        'effect': 'coins',
        'value': 100,
        'chance': 5
    },
    'вор': {
        'name': '🦝 Воришка',
        'description': 'Хитрый енот украл монеты!',
        'effect': 'coins',
        'value': -30,
        'chance': 5
    },
    'помощник': {
        'name': '🤝 Сосед помог',
        'description': 'Соседний фермер поделился опытом!',
        'effect': 'exp',
        'value': 25,
        'chance': 8
    },
    'магазин': {
        'name': '🏪 Скидка в магазине!',
        'description': 'Тебе вернули часть монет за покупку!',
        'effect': 'refund',
        'value': 20,
        'chance': 7
    },
    'подарок': {
        'name': '🎁 Загадочный подарок',
        'description': 'Ты получил загадочный подарок!',
        'effect': 'gift',
        'value': 50,
        'chance': 6
    }
}

def get_random_weather():
    """Получить случайную погоду"""
    total_chance = sum(event['chance'] for event in WEATHER_EVENTS.values())
    rand = random.randint(1, total_chance)
    
    current = 0
    for weather_name, weather_data in WEATHER_EVENTS.items():
        current += weather_data['chance']
        if rand <= current:
            return weather_name, weather_data
    
    return 'солнечно', WEATHER_EVENTS['солнечно']

def get_random_event():
    """Получить случайное событие"""
    total_chance = sum(event['chance'] for event in RANDOM_EVENTS.values())
    rand = random.randint(1, total_chance)
    
    current = 0
    for event_name, event_data in RANDOM_EVENTS.items():
        current += event_data['chance']
        if rand <= current:
            return event_name, event_data
    
    return None, None

def apply_weather_effect(user_id: int, weather_name: str, weather_data: dict):
    """Применить эффект погоды"""
    user = get_user(user_id)
    effect = weather_data['effect']
    value = weather_data['effect_value']
    message = f"{weather_data['name']}\n{weather_data['description']}\n\n"
    
    if effect == 'bonus':
        message += f"✨ Урожайность увеличена на {value}% на следующий сбор!"
        return message, 'harvest_bonus', value
    
    elif effect == 'water':
        if user.planted_crop:
            message += f"💧 Растения политы! Время созревания уменьшено на {value}%"
            return message, 'speed_bonus', value
        else:
            return f"{weather_data['name']}\n🌧️ Дождь прошёл, но на поле ничего не посажено!", None, 0
    
    elif effect == 'damage':
        if user.planted_crop:
            message += f"⚠️ Урожай повреждён! Потеряно {abs(value)}% урожая при сборе"
            return message, 'damage', value
        else:
            return f"{weather_data['name']}\n⚠️ Погода испортилась, но поле пустое!", None, 0
    
    elif effect == 'steal':
        lost = min(abs(value), user.coins)
        new_coins = user.coins - lost
        update_user(user_id, coins=new_coins)
        message += f"💨 Ты потерял {lost} монет!\n💰 Баланс: {new_coins}"
        return message, None, 0
    
    elif effect == 'luck':
        bonus = random.randint(20, 100)
        new_coins = user.coins + bonus
        update_user(user_id, coins=new_coins)
        message += f"🍀 Тебе улыбнулась удача! +{bonus}💰\n💰 Баланс: {new_coins}"
        return message, None, 0
    
    elif effect == 'mystery':
        rand_effect = random.choice(['coins', 'exp', 'nothing'])
        if rand_effect == 'coins':
            bonus = random.randint(10, 50)
            new_coins = user.coins + bonus
            update_user(user_id, coins=new_coins)
            message += f"✨ Ты нашёл {bonus} монет!\n💰 Баланс: {new_coins}"
        elif rand_effect == 'exp':
            bonus = random.randint(10, 30)
            new_exp = user.exp + bonus
            update_user(user_id, exp=new_exp)
            message += f"✨ Ты получил {bonus} опыта!\n📊 Опыт: {new_exp}/{user.level*100}"
        else:
            message += "✨ Ничего не произошло... но день был интересным!"
        return message, None, 0
    
    elif effect == 'disaster':
        lost = min(abs(value), user.coins)
        new_coins = user.coins - lost
        update_user(user_id, coins=new_coins)
        message += f"💥 Ферма пострадала! Ты потерял {lost} монет\n💰 Баланс: {new_coins}"
        if user.planted_crop:
            update_user(user_id, planted_crop=None, planted_at=None)
            message += f"\n🌾 Урожай полностью уничтожен!"
        return message, None, 0
    
    return message, None, 0

def apply_random_event(user_id: int, event_name: str, event_data: dict) -> str:
    """Применить случайное событие"""
    user = get_user(user_id)
    effect = event_data['effect']
    value = event_data['value']
    message = f"{event_data['name']}\n{event_data['description']}\n\n"
    
    if effect == 'coins':
        if value > 0:
            new_coins = user.coins + value
            update_user(user_id, coins=new_coins)
            message += f"💰 +{value} монет!\n💰 Баланс: {new_coins}"
        else:
            lost = min(abs(value), user.coins)
            new_coins = user.coins - lost
            update_user(user_id, coins=new_coins)
            message += f"💰 -{lost} монет!\n💰 Баланс: {new_coins}"
        return message
    
    elif effect == 'exp':
        new_exp = user.exp + value
        level_up = False
        new_level = user.level
        while new_exp >= new_level * 100:
            new_exp -= new_level * 100
            new_level += 1
            level_up = True
        
        update_user(user_id, exp=new_exp, level=new_level)
        message += f"✨ +{value} опыта!\n📊 Опыт: {new_exp}/{new_level*100}"
        
        if level_up:
            message += f"\n\n🏆 **ПОВЫШЕНИЕ УРОВНЯ!**\nТеперь ты {new_level} уровень! 🎉"
        return message
    
    elif effect == 'refund':
        bonus = random.randint(10, value)
        new_coins = user.coins + bonus
        update_user(user_id, coins=new_coins)
        message += f"🏷️ Тебе вернули {bonus} монет!\n💰 Баланс: {new_coins}"
        return message
    
    elif effect == 'gift':
        gift_type = random.choice(['coins', 'exp', 'diamonds'])
        if gift_type == 'coins':
            gift_value = random.randint(30, 100)
            new_coins = user.coins + gift_value
            update_user(user_id, coins=new_coins)
            message += f"🎁 Ты получил {gift_value} монет!\n💰 Баланс: {new_coins}"
        elif gift_type == 'exp':
            gift_value = random.randint(20, 60)
            new_exp = user.exp + gift_value
            update_user(user_id, exp=new_exp)
            message += f"🎁 Ты получил {gift_value} опыта!\n📊 Опыт: {new_exp}/{user.level*100}"
        else:
            gift_value = random.randint(1, 5)
            new_diamonds = user.diamonds + gift_value
            update_user(user_id, diamonds=new_diamonds)
            message += f"🎁 Ты получил {gift_value} алмазов!\n💎 Алмазы: {new_diamonds}"
        return message
    
    return message

def check_and_trigger_event(user_id: int):
    """Проверить и запустить случайное событие"""
    # 30% шанс на событие при каждом действии
    if random.random() > 0.3:
        return None
    
    # Выбираем тип события (70% погода, 30% случайное)
    if random.random() < 0.7:
        # Погодное событие
        weather_name, weather_data = get_random_weather()
        message, effect, value = apply_weather_effect(user_id, weather_name, weather_data)
        return f"🌤️ **СЛУЧАЙНОЕ СОБЫТИЕ!**\n\n{message}"
    else:
        # Случайное событие
        event_name, event_data = get_random_event()
        if event_data:
            message = apply_random_event(user_id, event_name, event_data)
            return f"🎲 **СЛУЧАЙНОЕ СОБЫТИЕ!**\n\n{message}"
    
    return None

def get_weather_forecast() -> str:
    """Получить прогноз погоды"""
    weather_name, weather_data = get_random_weather()
    
    messages = {
        'солнечно': "☀️ Сегодня солнечно! Отличный день для фермерства!",
        'дождь': "🌧️ Ожидается дождь. Растения будут рады!",
        'град': "🌨️ Возможен град. Береги урожай!",
        'ветер': "💨 Будет ветрено. Закрепи всё покрепче!",
        'радуга': "🌈 Сегодня будет радуга! День удачный!",
        'туман': "🌫️ Ожидается туман. Будь осторожен!",
        'жара': "🔥 Будет жарко. Не забудь полить растения!",
        'ураган': "🌀 Ожидается ураган! Лучше остаться дома!"
    }
    
    return messages.get(weather_name, "☀️ Хорошая погода для фермы!")