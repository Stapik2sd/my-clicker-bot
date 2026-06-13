# database.py
import sqlite3
import time
from typing import Optional, Dict, List, Tuple
from models import User, Crop, Animal, Upgrade

DB_PATH = "farm_bot.db"

def init_db():
    """Инициализация всех таблиц базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 100,
            diamonds INTEGER DEFAULT 0,
            skin TEXT DEFAULT '👨‍🌾 Фермер',
            planted_crop TEXT,
            planted_at INTEGER,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            last_daily INTEGER,
            daily_streak INTEGER DEFAULT 0,
            nickname TEXT,
            avatar TEXT DEFAULT '👨‍🌾',
            achievements TEXT,
            total_harvests INTEGER DEFAULT 0,
            total_crops_planted INTEGER DEFAULT 0,
            current_field INTEGER DEFAULT 1,
            last_animal_collect INTEGER,
            active_event TEXT,
            event_end_time INTEGER,
            soil_type TEXT DEFAULT 'обычная',
            seed_type TEXT DEFAULT 'обычные',
            garden_level INTEGER DEFAULT 1,
            current_location TEXT DEFAULT 'Обычная ферма'
        )
    ''')
    
    # Таблица улучшений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upgrades (
            user_id INTEGER PRIMARY KEY,
            harvest_bonus INTEGER DEFAULT 0,
            speed_bonus INTEGER DEFAULT 0,
            auto_water INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица животных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            user_id INTEGER,
            animal_type TEXT,
            count INTEGER DEFAULT 0,
            last_collect INTEGER,
            PRIMARY KEY (user_id, animal_type)
        )
    ''')
    
    # Таблица друзей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            since INTEGER,
            PRIMARY KEY (user_id, friend_id)
        )
    ''')
    
    # Таблица заявок в друзья
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            from_id INTEGER,
            to_id INTEGER,
            timestamp INTEGER,
            PRIMARY KEY (from_id, to_id)
        )
    ''')
    
    # Таблица статистики казино
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS casino_stats (
            user_id INTEGER PRIMARY KEY,
            total_bet INTEGER DEFAULT 0,
            total_win INTEGER DEFAULT 0,
            total_games INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица купленных локаций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_locations (
            user_id INTEGER,
            location_name TEXT,
            purchased_at INTEGER,
            PRIMARY KEY (user_id, location_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(user_id: int) -> User:
    """Получить пользователя из БД"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, coins, diamonds, skin, planted_crop, planted_at, 
               level, exp, last_daily, daily_streak, nickname, avatar, 
               achievements, total_harvests, total_crops_planted, current_field,
               last_animal_collect, active_event, event_end_time,
               soil_type, seed_type, garden_level, current_location
        FROM users WHERE user_id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    
    if row:
        user = User(
            user_id=row[0],
            coins=row[1],
            diamonds=row[2] or 0,
            skin=row[3] or "👨‍🌾 Фермер",
            planted_crop=row[4],
            planted_at=row[5],
            level=row[6],
            exp=row[7],
            last_daily=row[8],
            daily_streak=row[9] or 0,
            nickname=row[10] or f"Фермер_{user_id}",
            avatar=row[11] or "👨‍🌾",
            achievements=row[12].split(',') if row[12] and row[12] != '' else [],
            total_harvests=row[13] or 0,
            total_crops_planted=row[14] or 0,
            current_field=row[15] or 1,
            last_animal_collect=row[16] or 0,
            active_event=row[17],
            event_end_time=row[18] or 0
        )
        # Добавляем атрибуты для сада
        user.soil_type = row[19] if len(row) > 19 else 'обычная'
        user.seed_type = row[20] if len(row) > 20 else 'обычные'
        user.garden_level = row[21] if len(row) > 21 else 1
        user.current_location = row[22] if len(row) > 22 else 'Обычная ферма'
    else:
        # Создаем нового пользователя
        nickname = f"Фермер_{user_id}"
        cursor.execute('''
            INSERT INTO users (user_id, coins, diamonds, skin, nickname, avatar, achievements, soil_type, seed_type, garden_level, current_location)
            VALUES (?, 100, 0, '👨‍🌾 Фермер', ?, '👨‍🌾', '', 'обычная', 'обычные', 1, 'Обычная ферма')
        ''', (user_id, nickname))
        conn.commit()
        user = User(user_id=user_id, nickname=nickname)
        user.soil_type = 'обычная'
        user.seed_type = 'обычные'
        user.garden_level = 1
        user.current_location = 'Обычная ферма'
    
    conn.close()
    return user

def update_user(user_id: int, **kwargs):
    """Обновить данные пользователя"""
    if not kwargs:
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Преобразуем список достижений в строку
    if 'achievements' in kwargs and isinstance(kwargs['achievements'], list):
        kwargs['achievements'] = ','.join(kwargs['achievements'])
    
    for key, value in kwargs.items():
        try:
            cursor.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, user_id))
        except:
            pass
    
    conn.commit()
    conn.close()

def get_upgrades(user_id: int) -> Dict:
    """Получить улучшения пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT harvest_bonus, speed_bonus, auto_water FROM upgrades WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row:
        upgrades = {'harvest_bonus': row[0], 'speed_bonus': row[1], 'auto_water': row[2]}
    else:
        cursor.execute('INSERT INTO upgrades (user_id, harvest_bonus, speed_bonus, auto_water) VALUES (?, 0, 0, 0)', (user_id,))
        conn.commit()
        upgrades = {'harvest_bonus': 0, 'speed_bonus': 0, 'auto_water': 0}
    
    conn.close()
    return upgrades

def update_upgrades(user_id: int, **kwargs):
    """Обновить улучшения"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for key, value in kwargs.items():
        if key in ['harvest_bonus', 'speed_bonus', 'auto_water']:
            cursor.execute(f'UPDATE upgrades SET {key} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()

def get_animals(user_id: int) -> Dict:
    """Получить животных пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT animal_type, count, last_collect FROM animals WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    animals = {}
    for animal_type, count, last_collect in rows:
        animals[animal_type] = {'count': count, 'last_collect': last_collect or 0}
    return animals

def add_animal(user_id: int, animal_type: str):
    """Добавить животное пользователю"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute('''
        INSERT OR REPLACE INTO animals (user_id, animal_type, count, last_collect)
        VALUES (?, ?, COALESCE((SELECT count + 1 FROM animals WHERE user_id = ? AND animal_type = ?), 1), ?)
    ''', (user_id, animal_type, user_id, animal_type, now))
    
    conn.commit()
    conn.close()

def update_animal_collect(user_id: int, animal_type: str, last_collect: int):
    """Обновить время сбора дохода с животного"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE animals SET last_collect = ? WHERE user_id = ? AND animal_type = ?',
                   (last_collect, user_id, animal_type))
    conn.commit()
    conn.close()

def get_friends(user_id: int) -> List[int]:
    """Получить список друзей"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT friend_id FROM friends WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_friend_requests(user_id: int) -> List[int]:
    """Получить список заявок в друзья"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT from_id FROM friend_requests WHERE to_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_friend_request(from_id: int, to_id: int) -> bool:
    """Добавить заявку в друзья"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем, нет ли уже заявки
    cursor.execute('SELECT * FROM friend_requests WHERE from_id = ? AND to_id = ?', (from_id, to_id))
    if cursor.fetchone():
        conn.close()
        return False
    
    cursor.execute('INSERT INTO friend_requests (from_id, to_id, timestamp) VALUES (?, ?, ?)',
                   (from_id, to_id, int(time.time())))
    conn.commit()
    conn.close()
    return True

def accept_friend_request(user_id: int, from_id: int) -> bool:
    """Принять заявку в друзья"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем наличие заявки
    cursor.execute('SELECT * FROM friend_requests WHERE from_id = ? AND to_id = ?', (from_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Добавляем в друзья обоим
    now = int(time.time())
    cursor.execute('INSERT INTO friends (user_id, friend_id, since) VALUES (?, ?, ?)', (user_id, from_id, now))
    cursor.execute('INSERT INTO friends (user_id, friend_id, since) VALUES (?, ?, ?)', (from_id, user_id, now))
    
    # Удаляем заявку
    cursor.execute('DELETE FROM friend_requests WHERE from_id = ? AND to_id = ?', (from_id, user_id))
    
    conn.commit()
    conn.close()
    return True

def reject_friend_request(user_id: int, from_id: int) -> bool:
    """Отклонить заявку в друзья"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM friend_requests WHERE from_id = ? AND to_id = ?', (from_id, user_id))
    conn.commit()
    conn.close()
    return True

def get_casino_stats(user_id: int) -> Tuple[int, int, int]:
    """Получить статистику казино"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT total_bet, total_win, total_games FROM casino_stats WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0], row[1], row[2]
    return 0, 0, 0

def update_casino_stats(user_id: int, bet: int, win: int = 0):
    """Обновить статистику казино"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO casino_stats (user_id, total_bet, total_win, total_games)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            total_bet = total_bet + ?,
            total_win = total_win + ?,
            total_games = total_games + 1
    ''', (user_id, bet, win, bet, win))
    
    conn.commit()
    conn.close()

def get_user_locations(user_id: int) -> List[str]:
    """Получить список купленных локаций пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT location_name FROM user_locations WHERE user_id = ?', (user_id,))
    locations = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Стартовая локация всегда есть
    if 'Обычная ферма' not in locations:
        locations.append('Обычная ферма')
    
    return locations

def add_user_location(user_id: int, location_name: str):
    """Добавить локацию пользователю"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_locations (user_id, location_name, purchased_at) VALUES (?, ?, ?)',
                   (user_id, location_name, int(time.time())))
    conn.commit()
    conn.close()