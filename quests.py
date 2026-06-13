# quests.py
import sqlite3
import time
from database import get_user, update_user, DB_PATH

# Ежедневные квесты
DAILY_QUESTS = {
    'harvest_5': {
        'name': '🌾 Урожайный день',
        'description': 'Собрать 5 урожаев',
        'target': 5,
        'reward_coins': 100,
        'reward_exp': 50,
        'type': 'harvest'
    },
    'plant_10': {
        'name': '🌱 Сеятель',
        'description': 'Посадить 10 растений',
        'target': 10,
        'reward_coins': 80,
        'reward_exp': 40,
        'type': 'plant'
    },
    'earn_500': {
        'name': '💰 Богатый урожай',
        'description': 'Заработать 500 монет',
        'target': 500,
        'reward_coins': 150,
        'reward_exp': 60,
        'type': 'earn'
    },
    'animals_3': {
        'name': '🐔 Зоопарк',
        'description': 'Купить 3 животных',
        'target': 3,
        'reward_coins': 120,
        'reward_exp': 45,
        'type': 'animals'
    },
    'casino_win': {
        'name': '🎲 Везунчик',
        'description': 'Выиграть в казино 2 раза',
        'target': 2,
        'reward_coins': 200,
        'reward_exp': 80,
        'type': 'casino'
    },
    'friends_3': {
        'name': '👥 Дружный',
        'description': 'Добавить 3 друзей',
        'target': 3,
        'reward_coins': 150,
        'reward_exp': 50,
        'type': 'friends'
    }
}

def init_quests_table():
    """Создать таблицу для квестов"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_quests
                 (user_id INTEGER,
                  quest_id TEXT,
                  progress INTEGER DEFAULT 0,
                  completed INTEGER DEFAULT 0,
                  date TEXT,
                  PRIMARY KEY (user_id, quest_id))''')
    conn.commit()
    conn.close()

def get_daily_quests(user_id: int):
    """Получить ежедневные квесты"""
    today = time.strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    quests = {}
    for quest_id, quest_data in DAILY_QUESTS.items():
        c.execute('SELECT progress, completed FROM user_quests WHERE user_id = ? AND quest_id = ? AND date = ?',
                  (user_id, quest_id, today))
        row = c.fetchone()
        if row:
            quests[quest_id] = {
                'progress': row[0],
                'completed': row[1],
                'data': quest_data
            }
        else:
            c.execute('INSERT INTO user_quests (user_id, quest_id, progress, completed, date) VALUES (?, ?, 0, 0, ?)',
                      (user_id, quest_id, today))
            quests[quest_id] = {
                'progress': 0,
                'completed': 0,
                'data': quest_data
            }
    
    conn.commit()
    conn.close()
    return quests

def update_quest_progress(user_id: int, quest_type: str, amount: int = 1):
    """Обновить прогресс квеста"""
    today = time.strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for quest_id, quest_data in DAILY_QUESTS.items():
        if quest_data['type'] == quest_type:
            c.execute('SELECT progress, completed FROM user_quests WHERE user_id = ? AND quest_id = ? AND date = ?',
                      (user_id, quest_id, today))
            row = c.fetchone()
            
            if row and not row[1]:
                new_progress = row[0] + amount
                completed = 1 if new_progress >= quest_data['target'] else 0
                
                c.execute('UPDATE user_quests SET progress = ?, completed = ? WHERE user_id = ? AND quest_id = ? AND date = ?',
                          (new_progress, completed, user_id, quest_id, today))
                
                if completed and not row[1]:
                    user = get_user(user_id)
                    update_user(user_id, 
                               coins=user.coins + quest_data['reward_coins'],
                               exp=user.exp + quest_data['reward_exp'])
    
    conn.commit()
    conn.close()

def get_quests_text(user_id: int) -> str:
    """Получить текст с квестами"""
    quests = get_daily_quests(user_id)
    msg = "📋 **ЕЖЕДНЕВНЫЕ КВЕСТЫ** 📋\n\n"
    
    for quest_id, quest in quests.items():
        data = quest['data']
        status = "✅" if quest['completed'] else "⏳"
        msg += f"{status} **{data['name']}**\n"
        msg += f"   {data['description']}\n"
        msg += f"   Прогресс: {quest['progress']}/{data['target']}\n"
        msg += f"   Награда: {data['reward_coins']}💰 +{data['reward_exp']}✨\n\n"
    
    # Подсчёт выполненных квестов
    completed = sum(1 for q in quests.values() if q['completed'])
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n✅ Выполнено: {completed}/{len(quests)} квестов"
    
    return msg