# game_logic.py
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any

import vk_api

from database import (
    get_user, update_user, get_upgrades, update_upgrades,
    get_animals, add_animal, update_animal_collect,
    get_friends, get_friend_requests, get_casino_stats, update_casino_stats
)
from game_data import CROPS, ANIMALS, SKINS, ACHIEVEMENTS
from utils import vk_sessions

def check_achievements(user_id: int, vk) -> Tuple[int, list]:
    """Проверить и выдать достижения"""
    user = get_user(user_id)
    unlocked = []
    reward_total = 0
    
    # Первый урожай
    if 'first_harvest' not in user.achievements and user.total_harvests >= 1:
        user.achievements.append('first_harvest')
        reward_total += 50
        unlocked.append('🌾 Первый урожай')
    
    # Миллионер
    if 'millionaire' not in user.achievements and user.coins >= 1000:
        user.achievements.append('millionaire')
        reward_total += 200
        unlocked.append('💰 Миллионер')
    
    # Уровни
    if 'level_5' not in user.achievements and user.level >= 5:
        user.achievements.append('level_5')
        reward_total += 300
        unlocked.append('🏆 Опытный фермер')
    
    if 'level_10' not in user.achievements and user.level >= 10:
        user.achievements.append('level_10')
        reward_total += 500
        unlocked.append('👑 Мастер-фермер')
    
    # Посадки
    if 'crops_10' not in user.achievements and user.total_crops_planted >= 10:
        user.achievements.append('crops_10')
        reward_total += 100
        unlocked.append('🌽 Сеятель')
    
    if 'crops_100' not in user.achievements and user.total_crops_planted >= 100:
        user.achievements.append('crops_100')
        reward_total += 500
        unlocked.append('🌾 Агроном')
    
    # Животные
    animals = get_animals(user_id)
    total_animals = sum(data['count'] for data in animals.values())
    
    if 'animals_5' not in user.achievements and total_animals >= 5:
        user.achievements.append('animals_5')
        reward_total += 200
        unlocked.append('🐣 Животновод')
    
    if 'animals_20' not in user.achievements and total_animals >= 20:
        user.achievements.append('animals_20')
        reward_total += 800
        unlocked.append('🐘 Зоопарк')
    
    # Друзья
    friends = get_friends(user_id)
    if 'friend_3' not in user.achievements and len(friends) >= 3:
        user.achievements.append('friend_3')
        reward_total += 150
        unlocked.append('👥 Дружный')
    
    if 'friend_10' not in user.achievements and len(friends) >= 10:
        user.achievements.append('friend_10')
        reward_total += 500
        unlocked.append('🤝 Популярный')
    
    # Дейли бонус
    if 'daily_7' not in user.achievements and user.daily_streak >= 7:
        user.achievements.append('daily_7')
        reward_total += 300
        unlocked.append('📅 Старожил')
    
    if reward_total > 0:
        user.coins += reward_total
        update_user(user_id, coins=user.coins, achievements=user.achievements)
    
    return reward_total, unlocked

def casino_game(user_id: int, bet: int) -> str:
    """Игра в казино"""
    if bet < 50:
        return "❌ Минимальная ставка 50 монет!"
    
    user = get_user(user_id)
    if user.coins < bet:
        return f"❌ Не хватает! У вас {user.coins} монет"
    
    roll = random.randint(1, 100)
    
    if roll <= 45:  # Проигрыш 45%
        new_coins = user.coins - bet
        update_user(user_id, coins=new_coins)
        update_casino_stats(user_id, bet, 0)
        return f"🎰 **ВЫ ПРОИГРАЛИ!**\nСтавка: {bet}💰\n💰 Баланс: {new_coins}"
    
    elif roll <= 70:  # Ничья 25%
        update_casino_stats(user_id, bet, bet)
        return f"🎰 **НИЧЬЯ!**\nСтавка: {bet}💰 возвращена\n💰 Баланс: {user.coins}"
    
    elif roll <= 90:  # Выигрыш x2 20%
        win = bet * 2
        new_coins = user.coins + win
        update_user(user_id, coins=new_coins)
        update_casino_stats(user_id, bet, win)
        return f"🎰 **ВЫ ВЫИГРАЛИ!** 🎉\nСтавка: {bet}💰 → Выигрыш: {win}💰\n💰 Баланс: {new_coins}"
    
    else:  # Джекпот x5 10%
        win = bet * 5
        new_coins = user.coins + win
        update_user(user_id, coins=new_coins)
        update_casino_stats(user_id, bet, win)
        return f"🎰 **ДЖЕКПОТ!** 🎉🎉🎉\nСтавка: {bet}💰 → Выигрыш: {win}💰\n💰 Баланс: {new_coins}"

def notify_when_ready(user_id: int, crop_name: str, ready_time: int, vk):
    """Уведомление о созревании урожая"""
    def notify():
        wait_time = ready_time - time.time()
        if wait_time > 0:
            time.sleep(wait_time)
            user = get_user(user_id)
            if user.planted_crop == crop_name:
                msg = f"🌾 Ваш урожай {crop_name} созрел!"
                try:
                    vk.messages.send(
                        user_id=user_id,
                        message=msg,
                        random_id=random.randint(1, 2**31)
                    )
                except:
                    pass
    
    thread = threading.Thread(target=notify)
    thread.daemon = True
    thread.start()