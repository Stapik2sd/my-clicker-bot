# gardening.py
import sqlite3
from database import get_user, update_user, DB_PATH

# Типы почвы
SOIL_TYPES = {
    'обычная': {'price': 0, 'bonus': 0, 'emoji': '🟫', 'level': 1},
    'плодородная': {'price': 500, 'bonus': 20, 'emoji': '🟤', 'level': 2},
    'волшебная': {'price': 2000, 'bonus': 50, 'emoji': '✨', 'level': 3},
    'алмазная': {'price': 5000, 'bonus': 100, 'emoji': '💎', 'level': 4},
    'золотая': {'price': 10000, 'bonus': 200, 'emoji': '👑', 'level': 5}
}

SEEDS = {
    'обычные': {'price': 0, 'bonus': 0, 'emoji': '🌱'},
    'улучшенные': {'price': 1000, 'bonus': 30, 'emoji': '🌿'},
    'элитные': {'price': 5000, 'bonus': 80, 'emoji': '🌻'},
    'легендарные': {'price': 15000, 'bonus': 150, 'emoji': '🌲'}
}

def init_gardening_table():
    """Создать таблицы для садоводства (без ошибок дублирования)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Проверяем и добавляем колонки, если их нет
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'soil_type' not in columns:
        try:
            c.execute('ALTER TABLE users ADD COLUMN soil_type TEXT DEFAULT "обычная"')
        except:
            pass
    
    if 'seed_type' not in columns:
        try:
            c.execute('ALTER TABLE users ADD COLUMN seed_type TEXT DEFAULT "обычные"')
        except:
            pass
    
    if 'garden_level' not in columns:
        try:
            c.execute('ALTER TABLE users ADD COLUMN garden_level INTEGER DEFAULT 1')
        except:
            pass
    
    conn.commit()
    conn.close()

def upgrade_soil(user_id: int, soil_type: str) -> tuple:
    """Улучшить почву"""
    if soil_type not in SOIL_TYPES:
        return False, "❌ Такой почвы нет!"
    
    soil = SOIL_TYPES[soil_type]
    user = get_user(user_id)
    
    current_soil = getattr(user, 'soil_type', 'обычная')
    current_level = SOIL_TYPES.get(current_soil, {}).get('level', 1)
    
    if soil['level'] <= current_level:
        return False, f"❌ У вас уже {current_soil} почва! Улучшайте дальше."
    
    if user.coins < soil['price']:
        return False, f"💰 Нужно {soil['price']} монет! У вас {user.coins}"
    
    update_user(user_id, coins=user.coins - soil['price'])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET soil_type = ? WHERE user_id = ?', (soil_type, user_id))
    conn.commit()
    conn.close()
    
    return True, f"✅ Почва улучшена до {soil['emoji']} {soil_type}!\n🌾 Бонус к урожаю: +{soil['bonus']}%"

def upgrade_seeds(user_id: int, seed_type: str) -> tuple:
    """Улучшить семена"""
    if seed_type not in SEEDS:
        return False, "❌ Такого типа семян нет!"
    
    seed = SEEDS[seed_type]
    user = get_user(user_id)
    
    current_seed = getattr(user, 'seed_type', 'обычные')
    if seed_type == current_seed:
        return False, f"❌ У вас уже {seed_type} семена!"
    
    if user.coins < seed['price']:
        return False, f"💰 Нужно {seed['price']} монет! У вас {user.coins}"
    
    update_user(user_id, coins=user.coins - seed['price'])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET seed_type = ? WHERE user_id = ?', (seed_type, user_id))
    conn.commit()
    conn.close()
    
    return True, f"✅ Семена улучшены до {seed['emoji']} {seed_type}!\n🌾 Бонус к урожаю: +{seed['bonus']}%"

def get_garden_text(user_id: int) -> str:
    """Получить информацию о саде"""
    user = get_user(user_id)
    soil_type = getattr(user, 'soil_type', 'обычная')
    seed_type = getattr(user, 'seed_type', 'обычные')
    soil = SOIL_TYPES.get(soil_type, SOIL_TYPES['обычная'])
    seed = SEEDS.get(seed_type, SEEDS['обычные'])
    
    total_bonus = soil['bonus'] + seed['bonus']
    
    msg = "🌻 **САДОВОДСТВО** 🌻\n\n"
    msg += f"🏡 **Участок**\n"
    msg += f"   Почва: {soil['emoji']} {soil_type} (+{soil['bonus']}%)\n"
    msg += f"   Семена: {seed['emoji']} {seed_type} (+{seed['bonus']}%)\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✨ **Общий бонус: +{total_bonus}%** к урожаю!\n\n"
    
    msg += "🏪 **УЛУЧШЕНИЯ:**\n"
    msg += "📝 Чтобы улучшить, напишите:\n"
    msg += "   улучшить почву <название>\n"
    msg += "   улучшить семена <название>\n\n"
    
    for soil_name, soil_data in SOIL_TYPES.items():
        if soil_data['price'] > 0 and soil_data['level'] > soil['level']:
            msg += f"   {soil_data['emoji']} {soil_name} — {soil_data['price']}💰 (+{soil_data['bonus']}%)\n"
    
    msg += "\n"
    for seed_name, seed_data in SEEDS.items():
        if seed_data['price'] > 0 and seed_name != seed_type:
            msg += f"   {seed_data['emoji']} {seed_name} — {seed_data['price']}💰 (+{seed_data['bonus']}%)\n"
    
    return msg