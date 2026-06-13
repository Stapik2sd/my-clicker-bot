# locations.py
import random
import time
import sqlite3
from database import get_user, update_user, DB_PATH

# Локации
LOCATIONS = {
    'Обычная ферма': {
        'emoji': '🏡',
        'description': 'Стандартная ферма с хорошей почвой',
        'bonus_harvest': 0,
        'bonus_speed': 0,
        'price': 0,
        'level_req': 1,
        'crops_allowed': ['🍅 Помидор', '🥔 Картошка', '🥕 Морковь', '🍓 Клубника', '🎃 Тыква', '🍉 Арбуз', '✨ Золотая морковь']
    },
    'Лесная ферма': {
        'emoji': '🌲',
        'description': 'Ферма в лесу. Грибы и ягоды растут лучше',
        'bonus_harvest': 15,
        'bonus_speed': -10,
        'price': 1000,
        'level_req': 3,
        'crops_allowed': ['🍄 Грибы', '🫐 Черника', '🌿 Травы', '🌰 Орехи']
    },
    'Горная ферма': {
        'emoji': '⛰️',
        'description': 'Высоко в горах. Редкие минералы и морозостойкие растения',
        'bonus_harvest': 25,
        'bonus_speed': -20,
        'price': 2500,
        'level_req': 5,
        'crops_allowed': ['🍃 Чай', '🌸 Лаванда', '💎 Кристаллы', '⛏️ Минералы']
    },
    'Прибрежная ферма': {
        'emoji': '🏖️',
        'description': 'У самого моря. Можно ловить рыбу и собирать жемчуг',
        'bonus_harvest': 10,
        'bonus_speed': -5,
        'price': 2000,
        'level_req': 4,
        'crops_allowed': ['🥥 Кокос', '🍍 Ананас', '🐚 Жемчуг', '🐟 Рыба']
    },
    'Вулканическая ферма': {
        'emoji': '🌋',
        'description': 'На склоне вулкана. Очень опасно, но прибыльно!',
        'bonus_harvest': 50,
        'bonus_speed': -30,
        'price': 5000,
        'level_req': 7,
        'crops_allowed': ['🔥 Огненный цветок', '⚡ Энергетический кристалл', '🐉 Драконье яблоко']
    },
    'Магическая ферма': {
        'emoji': '✨',
        'description': 'В зачарованном лесу. Растут волшебные растения',
        'bonus_harvest': 40,
        'bonus_speed': -25,
        'price': 4000,
        'level_req': 6,
        'crops_allowed': ['🔮 Магическая морковь', '🍄 Светящийся гриб', '🌙 Лунный цветок']
    },
    'Подземная ферма': {
        'emoji': '🕳️',
        'description': 'Под землёй. Светятся растения и редкие грибы',
        'bonus_harvest': 30,
        'bonus_speed': -15,
        'price': 3000,
        'level_req': 5,
        'crops_allowed': ['💡 Светящийся мох', '🍄 Алмазный гриб', '🪨 Каменный плод']
    },
    'Космическая ферма': {
        'emoji': '🚀',
        'description': 'В открытом космосе! Инопланетные растения',
        'bonus_harvest': 100,
        'bonus_speed': -50,
        'price': 10000,
        'level_req': 10,
        'crops_allowed': ['👽 Инопланетный цветок', '🌠 Звездная пыльца', '🪐 Кольцо Сатурна']
    }
}

# Новые культуры для локаций
LOCATION_CROPS = {
    '🍄 Грибы': {'seed_price': 30, 'harvest_price': 80, 'grow_seconds': 45, 'emoji': '🍄', 'exp': 8},
    '🫐 Черника': {'seed_price': 25, 'harvest_price': 70, 'grow_seconds': 40, 'emoji': '🫐', 'exp': 7},
    '🌿 Травы': {'seed_price': 20, 'harvest_price': 60, 'grow_seconds': 35, 'emoji': '🌿', 'exp': 6},
    '🌰 Орехи': {'seed_price': 40, 'harvest_price': 100, 'grow_seconds': 50, 'emoji': '🌰', 'exp': 10},
    '🍃 Чай': {'seed_price': 35, 'harvest_price': 90, 'grow_seconds': 45, 'emoji': '🍃', 'exp': 9},
    '🌸 Лаванда': {'seed_price': 30, 'harvest_price': 85, 'grow_seconds': 40, 'emoji': '🌸', 'exp': 8},
    '💎 Кристаллы': {'seed_price': 100, 'harvest_price': 300, 'grow_seconds': 120, 'emoji': '💎', 'exp': 30},
    '⛏️ Минералы': {'seed_price': 80, 'harvest_price': 200, 'grow_seconds': 90, 'emoji': '⛏️', 'exp': 25},
    '🥥 Кокос': {'seed_price': 50, 'harvest_price': 150, 'grow_seconds': 70, 'emoji': '🥥', 'exp': 15},
    '🍍 Ананас': {'seed_price': 60, 'harvest_price': 180, 'grow_seconds': 80, 'emoji': '🍍', 'exp': 18},
    '🐚 Жемчуг': {'seed_price': 200, 'harvest_price': 600, 'grow_seconds': 180, 'emoji': '🐚', 'exp': 50},
    '🐟 Рыба': {'seed_price': 40, 'harvest_price': 120, 'grow_seconds': 60, 'emoji': '🐟', 'exp': 12},
    '🔥 Огненный цветок': {'seed_price': 300, 'harvest_price': 1000, 'grow_seconds': 240, 'emoji': '🔥', 'exp': 80},
    '⚡ Энергетический кристалл': {'seed_price': 500, 'harvest_price': 2000, 'grow_seconds': 360, 'emoji': '⚡', 'exp': 150},
    '🐉 Драконье яблоко': {'seed_price': 1000, 'harvest_price': 4000, 'grow_seconds': 600, 'emoji': '🐉', 'exp': 300},
    '🔮 Магическая морковь': {'seed_price': 200, 'harvest_price': 700, 'grow_seconds': 150, 'emoji': '🔮', 'exp': 50},
    '🍄 Светящийся гриб': {'seed_price': 150, 'harvest_price': 500, 'grow_seconds': 120, 'emoji': '🍄', 'exp': 40},
    '🌙 Лунный цветок': {'seed_price': 250, 'harvest_price': 800, 'grow_seconds': 180, 'emoji': '🌙', 'exp': 60},
    '💡 Светящийся мох': {'seed_price': 80, 'harvest_price': 250, 'grow_seconds': 100, 'emoji': '💡', 'exp': 25},
    '🍄 Алмазный гриб': {'seed_price': 400, 'harvest_price': 1500, 'grow_seconds': 300, 'emoji': '🍄', 'exp': 100},
    '🪨 Каменный плод': {'seed_price': 120, 'harvest_price': 350, 'grow_seconds': 140, 'emoji': '🪨', 'exp': 35},
    '👽 Инопланетный цветок': {'seed_price': 2000, 'harvest_price': 8000, 'grow_seconds': 1200, 'emoji': '👽', 'exp': 500},
    '🌠 Звездная пыльца': {'seed_price': 1500, 'harvest_price': 6000, 'grow_seconds': 900, 'emoji': '🌠', 'exp': 400},
    '🪐 Кольцо Сатурна': {'seed_price': 3000, 'harvest_price': 15000, 'grow_seconds': 1800, 'emoji': '🪐', 'exp': 1000}
}

def init_locations_table():
    """Создать таблицу для локаций пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Добавляем колонку текущей локации
    try:
        c.execute('ALTER TABLE users ADD COLUMN current_location TEXT DEFAULT "Обычная ферма"')
    except:
        pass
    
    # Таблица купленных локаций
    c.execute('''CREATE TABLE IF NOT EXISTS user_locations
                 (user_id INTEGER,
                  location_name TEXT,
                  purchased_at INTEGER,
                  PRIMARY KEY (user_id, location_name))''')
    
    conn.commit()
    conn.close()

def get_user_locations(user_id: int):
    """Получить список купленных локаций пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT location_name FROM user_locations WHERE user_id = ?', (user_id,))
    locations = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Стартовая локация всегда есть
    if 'Обычная ферма' not in locations:
        locations.append('Обычная ферма')
    
    return locations

def buy_location(user_id: int, location_name: str):
    """Купить новую локацию"""
    if location_name not in LOCATIONS:
        return False, "❌ Такой локации не существует!"
    
    location = LOCATIONS[location_name]
    user = get_user(user_id)
    
    # Проверяем уровень
    if user.level < location['level_req']:
        return False, f"❌ Нужен {location['level_req']} уровень! У вас {user.level}"
    
    # Проверяем, не куплена ли уже
    user_locations = get_user_locations(user_id)
    if location_name in user_locations:
        return False, "❌ У вас уже есть эта локация!"
    
    # Проверяем монеты
    if user.coins < location['price']:
        return False, f"💰 Нужно {location['price']} монет! У вас {user.coins}"
    
    # Покупаем
    update_user(user_id, coins=user.coins - location['price'])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO user_locations (user_id, location_name, purchased_at) VALUES (?, ?, ?)',
              (user_id, location_name, int(time.time())))
    conn.commit()
    conn.close()
    
    return True, f"✅ Куплена локация: {location['emoji']} {location_name}!\n{location['description']}\n💰 -{location['price']} монет"

def change_location(user_id: int, location_name: str):
    """Сменить текущую локацию"""
    if location_name not in LOCATIONS:
        return False, "❌ Такой локации не существует!"
    
    user_locations = get_user_locations(user_id)
    if location_name not in user_locations:
        return False, f"❌ У вас нет локации {location_name}! Купите её сначала."
    
    update_user(user_id, current_location=location_name)
    location = LOCATIONS[location_name]
    
    return True, f"🗺️ Вы переместились в {location['emoji']} **{location_name}**!\n\n{location['description']}\n\n✨ Бонусы локации:\n   +{location['bonus_harvest']}% к урожаю\n   -{abs(location['bonus_speed'])}% времени роста"

def get_locations_list_text(user_id: int):
    """Получить список всех локаций"""
    user = get_user(user_id)
    user_locations = get_user_locations(user_id)
    current_location = getattr(user, 'current_location', 'Обычная ферма')
    
    msg = "🗺️ **ЛОКАЦИИ** 🗺️\n\n"
    msg += f"📍 Текущая локация: **{current_location}**\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for loc_name, loc_data in LOCATIONS.items():
        owned = "✅" if loc_name in user_locations else "🔒"
        current = "👉 " if loc_name == current_location else ""
        
        msg += f"{current}{owned} {loc_data['emoji']} **{loc_name}**\n"
        msg += f"   {loc_data['description']}\n"
        
        if loc_name not in user_locations:
            msg += f"   💰 Цена: {loc_data['price']} монет\n"
            msg += f"   ⭐ Требуется: {loc_data['level_req']} уровень\n"
        else:
            msg += f"   ✨ Бонусы: +{loc_data['bonus_harvest']}% урожая, -{abs(loc_data['bonus_speed'])}% времени\n"
        
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 Команды:\n"
    msg += "   купить локацию <название>\n"
    msg += "   перейти в <название>\n"
    msg += "   моя локация"
    
    return msg

def get_location_bonus(user_id: int):
    """Получить бонусы текущей локации"""
    user = get_user(user_id)
    current_location = getattr(user, 'current_location', 'Обычная ферма')
    location = LOCATIONS.get(current_location, LOCATIONS['Обычная ферма'])
    
    return location['bonus_harvest'], location['bonus_speed']

def get_location_crops(user_id: int):
    """Получить список культур для текущей локации"""
    user = get_user(user_id)
    current_location = getattr(user, 'current_location', 'Обычная ферма')
    location = LOCATIONS.get(current_location, LOCATIONS['Обычная ферма'])
    
    return location['crops_allowed']