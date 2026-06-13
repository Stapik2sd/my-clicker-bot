# game_stats.py
import sqlite3
from datetime import datetime
from database import get_user, DB_PATH

def get_detailed_stats(user_id: int) -> str:
    """Получить подробную статистику"""
    user = get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Квесты
    c.execute('SELECT COUNT(*) FROM user_quests WHERE user_id = ? AND completed = 1', (user_id,))
    row = c.fetchone()
    completed_quests = row[0] if row else 0
    
    # Животные
    c.execute('SELECT SUM(count) FROM animals WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    animal_count = row[0] if row and row[0] else 0
    
    # Друзья
    c.execute('SELECT COUNT(*) FROM friends WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    friends_count = row[0] if row else 0
    
    # Казино
    c.execute('SELECT total_bet, total_win, total_games FROM casino_stats WHERE user_id = ?', (user_id,))
    casino = c.fetchone()
    
    conn.close()
    
    # Бонус от сада
    soil_type = getattr(user, 'soil_type', 'обычная')
    seed_type = getattr(user, 'seed_type', 'обычные')
    
    soil_bonus = 0
    seed_bonus = 0
    
    if soil_type == 'плодородная':
        soil_bonus = 20
    elif soil_type == 'волшебная':
        soil_bonus = 50
    elif soil_type == 'алмазная':
        soil_bonus = 100
    elif soil_type == 'золотая':
        soil_bonus = 200
    
    if seed_type == 'улучшенные':
        seed_bonus = 30
    elif seed_type == 'элитные':
        seed_bonus = 80
    elif seed_type == 'легендарные':
        seed_bonus = 150
    
    total_bonus = soil_bonus + seed_bonus
    
    msg = "📊 **ДЕТАЛЬНАЯ СТАТИСТИКА** 📊\n\n"
    msg += f"👤 **Игрок:** {user.avatar} {user.nickname}\n"
    msg += f"🆔 **ID:** {user_id}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🏆 **Уровень:** {user.level}\n"
    msg += f"📊 **Опыт:** {user.exp}/{user.level*100}\n"
    msg += f"💰 **Монет:** {user.coins}\n"
    msg += f"💎 **Алмазов:** {user.diamonds}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌾 **Собрано урожаев:** {user.total_harvests}\n"
    msg += f"🌱 **Посажено растений:** {user.total_crops_planted}\n"
    msg += f"🐔 **Куплено животных:** {animal_count}\n"
    msg += f"👥 **Друзей:** {friends_count}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌻 **Бонус сада:** +{total_bonus}% к урожаю\n"
    msg += f"🏅 **Достижений:** {len(user.achievements)}\n"
    msg += f"📋 **Выполнено квестов:** {completed_quests}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    
    if casino:
        total_bet, total_win, total_games = casino
        profit = total_win - total_bet
        msg += f"🎰 **Казино:**\n"
        msg += f"   Сыграно игр: {total_games}\n"
        msg += f"   Сумма ставок: {total_bet}\n"
        msg += f"   Сумма выигрышей: {total_win}\n"
        msg += f"   Профит: {profit:+}💰\n"
    else:
        msg += f"🎰 **Казино:**\n"
        msg += f"   Ещё не играли\n"
    
    msg += f"\n📅 **Дней подряд:** {user.daily_streak}\n"
    msg += f"🎁 **До следующего бонуса:** {24 - datetime.now().hour} ч"
    
    return msg

def get_leaderboard_stats() -> str:
    """Получить общую статистику сервера"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM users')
    row = c.fetchone()
    total_players = row[0] if row else 0
    
    c.execute('SELECT AVG(level) FROM users')
    row = c.fetchone()
    avg_level = row[0] if row and row[0] else 0
    
    c.execute('SELECT SUM(coins) FROM users')
    row = c.fetchone()
    total_coins = row[0] if row and row[0] else 0
    
    c.execute('SELECT SUM(total_harvests) FROM users')
    row = c.fetchone()
    total_harvests = row[0] if row and row[0] else 0
    
    c.execute('SELECT nickname, level, coins FROM users ORDER BY level DESC, coins DESC LIMIT 1')
    top_player = c.fetchone()
    
    conn.close()
    
    msg = "📊 **СТАТИСТИКА СЕРВЕРА** 📊\n\n"
    msg += f"👥 **Всего игроков:** {total_players}\n"
    msg += f"🏆 **Средний уровень:** {avg_level:.1f}\n"
    msg += f"💰 **Всего монет:** {int(total_coins):,}\n"
    msg += f"🌾 **Всего собрано:** {total_harvests}\n"
    
    if top_player:
        msg += f"\n👑 **Топ игрок:**\n"
        msg += f"   {top_player[0]} — {top_player[1]} уровень, {top_player[2]}💰"
    
    return msg