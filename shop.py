# shop.py
import sqlite3
import time
from database import get_user, update_user, DB_PATH

# Товары в магазине
SHOP_ITEMS = {
    'fertilizer': {
        'name': '🌿 Удобрение',
        'price': 50,
        'effect': 'Ускоряет рост на 50%',
        'type': 'fertilizer',
        'duration': 1
    },
    'insurance': {
        'name': '🛡️ Страховка урожая',
        'price': 200,
        'effect': 'Защищает от негативных событий',
        'type': 'insurance',
        'duration': 3
    },
    'double_harvest': {
        'name': '🌟 Двойной урожай',
        'price': 500,
        'effect': 'Следующий урожай даст в 2 раза больше',
        'type': 'double',
        'duration': 1
    },
    'energy_drink': {
        'name': '⚡ Энергетик',
        'price': 100,
        'effect': 'Мгновенно собирает урожай',
        'type': 'instant',
        'duration': 1
    },
    'lucky_coin': {
        'name': '🍀 Счастливая монета',
        'price': 300,
        'effect': '+20% к выигрышу в казино',
        'type': 'luck',
        'duration': 5
    },
    'watering_can': {
        'name': '💧 Волшебная лейка',
        'price': 150,
        'effect': 'Автополив на 1 день',
        'type': 'auto_water',
        'duration': 1
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

def buy_item(user_id: int, item_id: str) -> tuple:
    """Купить предмет из магазина"""
    if item_id not in SHOP_ITEMS:
        return False, "❌ Товар не найден!"
    
    item = SHOP_ITEMS[item_id]
    user = get_user(user_id)
    
    if user.coins < item['price']:
        return False, f"💰 Не хватает! Нужно {item['price']} монет. У вас {user.coins}"
    
    update_user(user_id, coins=user.coins - item['price'])
    
    # Сохраняем предмет в инвентарь
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO inventory (user_id, item_id, count) VALUES (?, ?, COALESCE((SELECT count + 1 FROM inventory WHERE user_id = ? AND item_id = ?), 1))',
              (user_id, item_id, user_id, item_id))
    conn.commit()
    conn.close()
    
    return True, f"✅ {item['name']} куплен! -{item['price']}💰\n📦 Эффект: {item['effect']}"

def use_item(user_id: int, item_id: str) -> tuple:
    """Использовать предмет"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT count FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    row = c.fetchone()
    
    if not row or row[0] <= 0:
        conn.close()
        return False, "❌ У вас нет этого предмета!"
    
    # Уменьшаем количество
    c.execute('UPDATE inventory SET count = count - 1 WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    
    # Добавляем эффект
    expires_at = int(time.time()) + (SHOP_ITEMS[item_id]['duration'] * 86400)  # в днях
    c.execute('INSERT OR REPLACE INTO active_effects (user_id, effect_id, expires_at) VALUES (?, ?, ?)',
              (user_id, item_id, expires_at))
    
    conn.commit()
    conn.close()
    
    return True, f"✨ Использован {SHOP_ITEMS[item_id]['name']}! {SHOP_ITEMS[item_id]['effect']}"

def get_shop_text() -> str:
    """Получить текст магазина"""
    msg = "🛍️ **МАГАЗИН ПРЕДМЕТОВ** 🛍️\n\n"
    for item_id, item in SHOP_ITEMS.items():
        msg += f"🔹 {item['name']} — {item['price']}💰\n"
        msg += f"   📦 Эффект: {item['effect']}\n"
        msg += f"   ⏱️ Длительность: {item['duration']} дн.\n\n"
    return msg

def get_inventory_text(user_id: int) -> str:
    """Получить текст инвентаря"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT item_id, count FROM inventory WHERE user_id = ? AND count > 0', (user_id,))
    items = c.fetchall()
    conn.close()
    
    if not items:
        return "📦 **ИНВЕНТАРЬ**\n\nУ вас пока нет предметов. Купите их в магазине!"
    
    msg = "📦 **ИНВЕНТАРЬ**\n\n"
    for item_id, count in items:
        if item_id in SHOP_ITEMS:
            msg += f"• {SHOP_ITEMS[item_id]['name']} — {count} шт.\n"
            msg += f"   {SHOP_ITEMS[item_id]['effect']}\n\n"
    
    msg += "\n💡 Чтобы использовать предмет, напишите: использовать <название>"
    return msg