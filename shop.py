# shop.py
import sqlite3
import time
from database import get_user, update_user, DB_PATH

# Товары в магазине
SHOP_ITEMS = {
    'fertilizer': {
        'name': 'Удобрение',
        'price': 50,
        'effect': 'Ускоряет рост на 50%',
        'type': 'fertilizer',
        'duration': 1,
        'emoji': '🌿'
    },
    'insurance': {
        'name': 'Страховка',
        'price': 200,
        'effect': 'Защищает от негативных событий',
        'type': 'insurance',
        'duration': 3,
        'emoji': '🛡️'
    },
    'double_harvest': {
        'name': 'Двойной урожай',
        'price': 500,
        'effect': 'Следующий урожай даст в 2 раза больше',
        'type': 'double',
        'duration': 1,
        'emoji': '🌟'
    },
    'energy_drink': {
        'name': 'Энергетик',
        'price': 100,
        'effect': 'Мгновенно собирает урожай',
        'type': 'instant',
        'duration': 1,
        'emoji': '⚡'
    },
    'lucky_coin': {
        'name': 'Счастливая монета',
        'price': 300,
        'effect': '+20% к выигрышу в казино',
        'type': 'luck',
        'duration': 5,
        'emoji': '🍀'
    },
    'watering_can': {
        'name': 'Волшебная лейка',
        'price': 150,
        'effect': 'Автополив на 1 день',
        'type': 'auto_water',
        'duration': 1,
        'emoji': '💧'
    },
    'magic_seed': {
        'name': 'Волшебное семя',
        'price': 1000,
        'effect': 'Мгновенно вырастает любой урожай',
        'type': 'magic',
        'duration': 1,
        'emoji': '✨'
    },
    'golden_hoe': {
        'name': 'Золотая мотыга',
        'price': 2000,
        'effect': '+50% к урожаю навсегда',
        'type': 'permanent',
        'duration': -1,
        'emoji': '👑'
    }
}

def init_shop_table():
    """Создать таблицу инвентаря"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (user_id INTEGER,
                  item_id TEXT,
                  count INTEGER DEFAULT 0,
                  PRIMARY KEY (user_id, item_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS active_effects
                 (user_id INTEGER,
                  effect_id TEXT,
                  expires_at INTEGER,
                  PRIMARY KEY (user_id, effect_id))''')
    conn.commit()
    conn.close()

def buy_item(user_id: int, item_name: str):
    """Купить предмет из магазина по названию"""
    # Ищем предмет по названию
    item_id = None
    item = None
    for iid, data in SHOP_ITEMS.items():
        if data['name'].lower() == item_name.lower() or item_name.lower() in data['name'].lower():
            item_id = iid
            item = data
            break
    
    if not item_id:
        return False, "❌ Товар не найден!\n\nДоступные предметы:\n• удобрение\n• страховка\n• двойной урожай\n• энергетик\n• счастливая монета\n• волшебная лейка\n• волшебное семя\n• золотая мотыга"
    
    user = get_user(user_id)
    
    if user.coins < item['price']:
        return False, f"💰 Не хватает! Нужно {item['price']} монет. У вас {user.coins}"
    
    # Списываем монеты
    update_user(user_id, coins=user.coins - item['price'])
    
    # Сохраняем предмет в инвентарь
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT count FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    row = c.fetchone()
    
    if row:
        new_count = row[0] + 1
        c.execute('UPDATE inventory SET count = ? WHERE user_id = ? AND item_id = ?', 
                  (new_count, user_id, item_id))
    else:
        c.execute('INSERT INTO inventory (user_id, item_id, count) VALUES (?, ?, 1)',
                  (user_id, item_id))
    
    conn.commit()
    conn.close()
    
    return True, f"✅ {item['emoji']} {item['name']} куплен!\n💰 -{item['price']} монет\n📦 Эффект: {item['effect']}"

def use_item(user_id: int, item_name: str):
    """Использовать предмет по названию"""
    # Ищем предмет по названию
    item_id = None
    item_data = None
    
    for iid, data in SHOP_ITEMS.items():
        if data['name'].lower() == item_name.lower() or item_name.lower() in data['name'].lower():
            item_id = iid
            item_data = data
            break
    
    if not item_id:
        return False, "❌ Предмет не найден! Доступные предметы: удобрение, страховка, двойной урожай, энергетик, счастливая монета, волшебная лейка, волшебное семя, золотая мотыга"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT count FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    row = c.fetchone()
    
    if not row or row[0] <= 0:
        conn.close()
        return False, f"❌ У вас нет {item_data['emoji']} {item_data['name']}! Купите его в магазине (напишите: купить {item_data['name']})"
    
    # Уменьшаем количество
    c.execute('UPDATE inventory SET count = count - 1 WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    
    # Добавляем эффект (если не перманентный)
    if item_data['duration'] > 0:
        expires_at = int(time.time()) + (item_data['duration'] * 86400)
        c.execute('INSERT OR REPLACE INTO active_effects (user_id, effect_id, expires_at) VALUES (?, ?, ?)',
                  (user_id, item_id, expires_at))
    
    conn.commit()
    conn.close()
    
    # Особый эффект для волшебного семени
    if item_id == 'magic_seed':
        user = get_user(user_id)
        if user.planted_crop:
            return True, f"✨ {item_data['emoji']} {item_data['name']} использован!\n🌾 Ваш урожай {user.planted_crop} созрел мгновенно!\n\n💡 Теперь нажмите 'Собрать'!"
        else:
            return True, f"✨ {item_data['emoji']} {item_data['name']} использован!\n🌱 При следующей посадке урожай созреет мгновенно!"
    
    return True, f"✨ {item_data['emoji']} {item_data['name']} использован!\n📦 {item_data['effect']}"

def get_shop_text() -> str:
    """Получить текст магазина"""
    msg = "🛍️ **МАГАЗИН ПРЕДМЕТОВ** 🛍️\n\n"
    msg += "💰 Чтобы купить, напишите: купить <название>\n"
    msg += "📦 Чтобы использовать, напишите: использовать <название>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for item_id, item in SHOP_ITEMS.items():
        msg += f"{item['emoji']} **{item['name']}** — {item['price']}💰\n"
        msg += f"   📦 {item['effect']}\n"
        if item['duration'] > 0:
            msg += f"   ⏱️ Длительность: {item['duration']} дн.\n"
        elif item['duration'] == -1:
            msg += f"   ♾️ Навсегда\n"
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 **Примеры:**\n"
    msg += "   купить удобрение\n"
    msg += "   использовать энергетик"
    
    return msg

def get_inventory_text(user_id: int) -> str:
    """Получить текст инвентаря"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT item_id, count FROM inventory WHERE user_id = ? AND count > 0', (user_id,))
    items = c.fetchall()
    
    # Получаем активные эффекты
    c.execute('SELECT effect_id, expires_at FROM active_effects WHERE user_id = ? AND expires_at > ?', 
              (user_id, int(time.time())))
    active_effects = c.fetchall()
    conn.close()
    
    if not items and not active_effects:
        return "📦 **ИНВЕНТАРЬ**\n\nУ вас пока нет предметов.\n\n💡 Купите их в магазине: напишите 'предметы'"
    
    msg = "📦 **ИНВЕНТАРЬ**\n\n"
    
    if items:
        msg += "🎒 **Предметы:**\n"
        for item_id, count in items:
            if item_id in SHOP_ITEMS:
                item = SHOP_ITEMS[item_id]
                msg += f"   {item['emoji']} {item['name']} — {count} шт.\n"
        msg += "\n"
    
    if active_effects:
        msg += "✨ **Активные эффекты:**\n"
        for effect_id, expires_at in active_effects:
            if effect_id in SHOP_ITEMS:
                item = SHOP_ITEMS[effect_id]
                time_left = expires_at - int(time.time())
                days_left = time_left // 86400
                hours_left = (time_left % 86400) // 3600
                msg += f"   {item['emoji']} {item['name']} — {days_left}д {hours_left}ч\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 **Использовать предмет:**\n"
    msg += "   использовать удобрение"
    
    return msg
