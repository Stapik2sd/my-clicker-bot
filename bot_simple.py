# bot.py
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import time
import random
from datetime import datetime, timedelta

from config import VK_TOKEN, GROUP_ID
from database import init_db, get_user, update_user, get_upgrades, update_upgrades, get_friends, get_friend_requests, get_animals, get_casino_stats
from game_data import ALL_CROPS, ANIMALS, SKINS, ACHIEVEMENTS
from game_logic import check_achievements, casino_game, notify_when_ready
from animals import buy_animal, collect_animal_income, get_my_animals_text, get_animal_shop_text
from friends import get_friends_list_text, get_friend_requests_text, send_friend_request, accept_request, reject_request, get_friends_keyboard_text
from events import check_and_trigger_event, get_weather_forecast
from quests import init_quests_table, get_quests_text, update_quest_progress
from shop import init_shop_table, get_shop_text, get_inventory_text
from gardening import init_gardening_table, get_garden_text
from mini_games import game_dice, game_coinflip, game_blackjack, get_games_text
from game_stats import get_detailed_stats, get_leaderboard_stats
from keyboards import get_main_keyboard, get_plant_keyboard, get_animals_keyboard, get_profile_keyboard, get_skins_keyboard, get_friends_keyboard, get_upgrade_keyboard, get_achievements_keyboard, get_casino_keyboard, get_locations_keyboard
from locations import init_locations_table, get_locations_list_text, buy_location, change_location, get_location_bonus, get_location_crops
from utils import vk_sessions

def send_message(vk, user_id: int, message: str, keyboard=None):
    """Отправить сообщение пользователю"""
    try:
        if keyboard:
            vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=random.randint(1, 2**31),
                keyboard=keyboard.get_keyboard()
            )
        else:
            vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=random.randint(1, 2**31)
            )
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def handle_message(user_id: int, text: str, vk):
    """Обработка сообщений"""
    text_lower = text.lower().strip()
    user = get_user(user_id)
    upgrades = get_upgrades(user_id)
    
    # Проверяем достижения
    reward, unlocked = check_achievements(user_id, vk)
    achievement_msg = ""
    if unlocked:
        achievement_msg = f"\n\n🏅 Получены достижения: {', '.join(unlocked)}! +{reward}💰"
    
    # ГЛАВНОЕ МЕНЮ
    if text_lower in ['ферма', 'старт', 'меню', 'начать', '◀ на главную', '◀ назад']:
        plant_status = f"🌱 {user.planted_crop}" if user.planted_crop else "🌾 Пусто"
        bar_length = 10
        filled = int((user.exp / (user.level * 100)) * bar_length) if user.level * 100 > 0 else 0
        progress_bar = "█" * filled + "░" * (bar_length - filled)
        
        animal_income, collected = collect_animal_income(user_id)
        animal_msg = f"\n🐔 Доход с животных: +{animal_income}💰" if animal_income > 0 else ""
        
        # Получаем текущую локацию
        current_location = getattr(user, 'current_location', 'Обычная ферма')
        
        msg = (
            f"🏡 **ВИРТУАЛЬНАЯ ФЕРМА**\n\n"
            f"👤 **{user.avatar} {user.nickname}**\n"
            f"🗺️ **Локация:** {current_location}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 **Монеты:** {user.coins} 🪙\n"
            f"💎 **Алмазы:** {user.diamonds} 💎\n"
            f"🏆 **Уровень:** {user.level}\n"
            f"📊 **Опыт:** {progress_bar} {user.exp}/{user.level*100}\n"
            f"🌾 **На поле:** {plant_status}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔧 **Улучшения:**\n"
            f"   🔨 +{upgrades['harvest_bonus']*5}% урожая\n"
            f"   ⚡ -{upgrades['speed_bonus']*5}% времени\n"
            f"   💧 {'✅' if upgrades['auto_water'] else '❌'} автополив\n"
            f"━━━━━━━━━━━━━━━━━━━━━{animal_msg}{achievement_msg}"
        )
        return msg, get_main_keyboard()
    
    # БАЛАНС
    elif text_lower in ['баланс', '💰 баланс']:
        return f"💰 **БАЛАНС**\n\n🪙 Монет: {user.coins}\n💎 Алмазов: {user.diamonds}", get_main_keyboard()
    
    # БОНУС
    elif text_lower in ['бонус', '🎁 бонус', 'ежедневный бонус']:
        today = datetime.now().date()
        last_daily = user.last_daily
        if last_daily and datetime.fromtimestamp(last_daily).date() == today:
            return "🎁 Бонус уже получен сегодня! Завтра будет новый.", get_main_keyboard()
        
        if last_daily and datetime.fromtimestamp(last_daily).date() == today - timedelta(days=1):
            streak = user.daily_streak + 1
        else:
            streak = 1
        
        bonus = min(50 + (streak - 1) * 10, 200)
        new_coins = user.coins + bonus
        update_user(user_id, coins=new_coins, last_daily=int(time.time()), daily_streak=streak)
        
        check_achievements(user_id, vk)
        
        return f"🎁 ЕЖЕДНЕВНЫЙ БОНУС! +{bonus}💰\n📅 Серия: {streak} дней\n💰 Баланс: {new_coins}", get_main_keyboard()
    
    # ПРОГНОЗ ПОГОДЫ
    elif text_lower in ['прогноз погоды', '🌤️ прогноз погоды', 'погода']:
        forecast = get_weather_forecast()
        return f"🌤️ **ПРОГНОЗ ПОГОДЫ**\n\n{forecast}", get_main_keyboard()
    
    # КВЕСТЫ
    elif text_lower in ['квесты', '📋 квесты']:
        msg = get_quests_text(user_id)
        return msg, get_main_keyboard()
    
    # МАГАЗИН ПРЕДМЕТОВ
    elif text_lower in ['предметы', '🛍️ предметы', 'магазин предметов']:
        msg = get_shop_text()
        return msg, get_main_keyboard()
    
    elif text_lower in ['инвентарь', '🎒 инвентарь', '📦 инвентарь']:
        msg = get_inventory_text(user_id)
        return msg, get_main_keyboard()
    
    # САДОВОДСТВО
    elif text_lower in ['сад', '🌻 сад', 'садоводство']:
        msg = get_garden_text(user_id)
        return msg, get_main_keyboard()
    
    # МИНИ-ИГРЫ
    elif text_lower in ['игры', '🎮 игры', 'мини-игры']:
        msg = get_games_text()
        return msg, get_main_keyboard()
    
    elif text_lower.startswith('кости '):
        try:
            bet = int(text_lower.replace('кости ', '').strip())
            result = game_dice(user_id, bet)
            return result, get_main_keyboard()
        except:
            return "❌ Пример: кости 100", get_main_keyboard()
    
    elif text_lower.startswith('орел '):
        try:
            bet = int(text_lower.replace('орел ', '').strip())
            result = game_coinflip(user_id, bet, 'орел')
            return result, get_main_keyboard()
        except:
            return "❌ Пример: орел 100", get_main_keyboard()
    
    elif text_lower.startswith('решка '):
        try:
            bet = int(text_lower.replace('решка ', '').strip())
            result = game_coinflip(user_id, bet, 'решка')
            return result, get_main_keyboard()
        except:
            return "❌ Пример: решка 100", get_main_keyboard()
    
    elif text_lower.startswith('блэкджек '):
        try:
            bet = int(text_lower.replace('блэкджек ', '').strip())
            result = game_blackjack(user_id, bet)
            return result, get_main_keyboard()
        except:
            return "❌ Пример: блэкджек 100", get_main_keyboard()
    
    # СТАТИСТИКА
    elif text_lower in ['моя статистика', '📊 моя статистика', 'детальная статистика', 'статистика моя']:
        msg = get_detailed_stats(user_id)
        return msg, get_main_keyboard()
    
    elif text_lower in ['статистика сервера', 'топ сервера', 'сервер']:
        msg = get_leaderboard_stats()
        return msg, get_main_keyboard()
    
    # ЖИВОТНЫЕ
    elif text_lower in ['животные', '🐔 животные']:
        animals_data = get_animals(user_id)
        if not animals_data:
            msg = get_animal_shop_text()
        else:
            msg = get_my_animals_text(user_id)
        return msg, get_animals_keyboard()
    
    # ПОКУПКА ЖИВОТНЫХ
    elif 'купить' in text_lower:
        if 'курица' in text_lower:
            success, msg = buy_animal(user_id, '🐔 Курица')
            return msg, get_animals_keyboard()
        elif 'корова' in text_lower:
            success, msg = buy_animal(user_id, '🐮 Корова')
            return msg, get_animals_keyboard()
        elif 'овца' in text_lower:
            success, msg = buy_animal(user_id, '🐑 Овца')
            return msg, get_animals_keyboard()
        elif 'свинья' in text_lower:
            success, msg = buy_animal(user_id, '🐷 Свинья')
            return msg, get_animals_keyboard()
        elif 'пчела' in text_lower:
            success, msg = buy_animal(user_id, '🐝 Пчела')
            return msg, get_animals_keyboard()
        elif 'утка' in text_lower:
            success, msg = buy_animal(user_id, '🦆 Утка')
            return msg, get_animals_keyboard()
    
    # Сбор дохода с животных
    elif text_lower in ['💰 собрать доход', 'собрать доход']:
        total_income, collected = collect_animal_income(user_id)
        if total_income > 0:
            user = get_user(user_id)
            msg = f"💰 **СОБРАНО!**\n\n"
            for c in collected[:5]:
                msg += f"{c}\n"
            msg += f"\n💰 Всего: +{total_income}💰\n🪙 Баланс: {user.coins}"
            return msg, get_animals_keyboard()
        else:
            return "⏳ Нет дохода для сбора! Подождите, пока животные принесут доход.", get_animals_keyboard()
    
    # ПРОФИЛЬ
    elif text_lower in ['профиль', '👤 профиль']:
        animals = get_animals(user_id)
        animal_count = sum(data['count'] for data in animals.values())
        friends_count = len(get_friends(user_id))
        msg = (
            f"👤 **ПРОФИЛЬ**\n\n"
            f"{user.avatar} **Ник:** {user.nickname}\n"
            f"🆔 **ID:** {user_id}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 **Уровень:** {user.level}\n"
            f"💰 **Монет:** {user.coins}\n"
            f"💎 **Алмазов:** {user.diamonds}\n"
            f"🐔 **Животных:** {animal_count}\n"
            f"👥 **Друзья:** {friends_count}\n"
            f"🏅 **Достижения:** {len(user.achievements)}/{len(ACHIEVEMENTS)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        return msg, get_profile_keyboard()
    
    # Смена ника
    elif text_lower in ['✏️ сменить ник (100💰)', 'сменить ник']:
        return "✏️ **СМЕНА НИКА**\n\nОтправь:\nник <новый ник>\n\n💰 Стоимость: 100 монет", get_profile_keyboard()
    
    elif text_lower.startswith('ник '):
        new_nick = text[4:].strip()
        if len(new_nick) > 30:
            return "❌ Слишком длинный ник! Максимум 30 символов.", get_profile_keyboard()
        if len(new_nick) < 2:
            return "❌ Слишком короткий ник! Минимум 2 символа.", get_profile_keyboard()
        if user.coins < 100:
            return f"💰 Не хватает монет! Нужно 100 монет. У вас {user.coins}", get_profile_keyboard()
        
        update_user(user_id, coins=user.coins - 100, nickname=new_nick)
        return f"✅ Ник изменён на {new_nick}! -100💰", get_profile_keyboard()
    
    # Смена скина
    elif text_lower in ['🎭 сменить скин', 'сменить скин']:
        msg = "🎭 **ВЫБЕРИ СКИН**\n\n"
        for skin_name, skin_data in SKINS.items():
            price_text = f" ({skin_data['price']}💰)" if skin_data['price'] > 0 else " (бесплатно)"
            msg += f"{skin_data['emoji']} {skin_name}{price_text}\n"
        return msg, get_skins_keyboard()
    
    elif any(skin_name in text for skin_name in SKINS.keys()):
        for skin_name, skin_data in SKINS.items():
            if skin_name in text:
                if skin_data['price'] > 0 and user.coins < skin_data['price']:
                    return f"💰 Не хватает монет! Нужно {skin_data['price']} монет", get_profile_keyboard()
                if skin_data['price'] > 0:
                    update_user(user_id, coins=user.coins - skin_data['price'], avatar=skin_data['emoji'], skin=skin_name)
                else:
                    update_user(user_id, avatar=skin_data['emoji'], skin=skin_name)
                return f"✅ Скин изменён на {skin_data['emoji']} {skin_name}!", get_profile_keyboard()
    
    # ДРУЗЬЯ
    elif text_lower in ['друзья', '👥 друзья']:
        return get_friends_keyboard_text(), get_friends_keyboard()
    
    elif text_lower == '➕ добавить друга' or text_lower == 'добавить друга':
        return "➕ **ДОБАВИТЬ ДРУГА**\n\nВведите ID друга:\nдруг 123456789", get_friends_keyboard()
    
    elif text_lower.startswith('друг '):
        try:
            friend_id = int(text[5:].strip())
            success, msg = send_friend_request(user_id, friend_id, vk)
            return msg, get_friends_keyboard()
        except ValueError:
            return "❌ Неправильный ID! Используйте: друг 123456789", get_friends_keyboard()
    
    elif text_lower in ['📩 заявки', 'заявки']:
        msg = get_friend_requests_text(user_id)
        return msg, get_friends_keyboard()
    
    elif text_lower.startswith('/принять '):
        try:
            from_id = int(text[9:].strip())
            success, msg = accept_request(user_id, from_id, vk)
            if success:
                check_achievements(user_id, vk)
            return msg, get_friends_keyboard()
        except ValueError:
            return "❌ Ошибка! Пример: /принять 123456789", get_friends_keyboard()
    
    elif text_lower.startswith('/отклонить '):
        try:
            from_id = int(text[11:].strip())
            success, msg = reject_request(user_id, from_id)
            return msg, get_friends_keyboard()
        except ValueError:
            return "❌ Ошибка! Пример: /отклонить 123456789", get_friends_keyboard()
    
    elif text_lower in ['👥 мои друзья', 'мои друзья']:
        msg = get_friends_list_text(user_id)
        return msg, get_friends_keyboard()
    
    # КАЗИНО
    elif text_lower in ['казино', '🎰 казино']:
        return f"🎰 **КАЗИНО** 🎰\n\n💰 Ваш баланс: {user.coins}💰\n\nВыберите ставку:", get_casino_keyboard()
    
    elif text_lower.startswith('🎲 '):
        try:
            bet = int(text_lower.replace('🎲 ', '').strip())
            if bet in [50, 100, 200, 500, 1000]:
                result = casino_game(user_id, bet)
                return result, get_casino_keyboard()
            else:
                return "❌ Доступные ставки: 50, 100, 200, 500, 1000", get_casino_keyboard()
        except:
            pass
    
    elif text_lower in ['📊 статистика казино', 'статистика казино']:
        total_bet, total_win, total_games = get_casino_stats(user_id)
        if total_games > 0:
            profit = total_win - total_bet
            winrate = (total_win / total_bet * 100) if total_bet > 0 else 0
            msg = (
                f"📊 **СТАТИСТИКА КАЗИНО**\n\n"
                f"🎲 Сыграно игр: {total_games}\n"
                f"💰 Сумма ставок: {total_bet}\n"
                f"🏆 Сумма выигрышей: {total_win}\n"
                f"📈 Профит: {profit:+}\n"
                f"📊 Возврат: {winrate:.1f}%"
            )
        else:
            msg = "📊 Нет статистики! Сыграйте в казино, чтобы появилась статистика."
        return msg, get_casino_keyboard()
    
    # МАГАЗИН УЛУЧШЕНИЙ
    elif text_lower in ['улучшения', '🏪 улучшения', 'магазин улучшений']:
        msg = (
            f"🏪 **МАГАЗИН УЛУЧШЕНИЙ**\n\n"
            f"💰 Баланс: {user.coins}💰\n\n"
            f"🔨 Урожайность ({upgrades['harvest_bonus']}/10): +5% к урожаю → 500💰\n"
            f"⚡ Скорость ({upgrades['speed_bonus']}/10): -5% времени роста → 300💰\n"
            f"💧 Автополив ({'✅' if upgrades['auto_water'] else '❌'}): автоматический сбор → 1000💰"
        )
        return msg, get_upgrade_keyboard()
    
    elif '🔨' in text:
        if upgrades['harvest_bonus'] >= 10:
            return "🔨 Максимальный уровень улучшения достигнут!", get_main_keyboard()
        if user.coins < 500:
            return f"💰 Не хватает монет! Нужно 500 монет. У вас {user.coins}", get_main_keyboard()
        
        update_upgrades(user_id, harvest_bonus=upgrades['harvest_bonus'] + 1)
        update_user(user_id, coins=user.coins - 500)
        return f"🔨 Урожайность улучшена! +{upgrades['harvest_bonus'] + 1} уровень (+{(upgrades['harvest_bonus'] + 1)*5}% урожая)", get_main_keyboard()
    
    elif '⚡' in text:
        if upgrades['speed_bonus'] >= 10:
            return "⚡ Максимальный уровень улучшения достигнут!", get_main_keyboard()
        if user.coins < 300:
            return f"💰 Не хватает монет! Нужно 300 монет. У вас {user.coins}", get_main_keyboard()
        
        update_upgrades(user_id, speed_bonus=upgrades['speed_bonus'] + 1)
        update_user(user_id, coins=user.coins - 300)
        return f"⚡ Скорость улучшена! +{upgrades['speed_bonus'] + 1} уровень (-{(upgrades['speed_bonus'] + 1)*5}% времени роста)", get_main_keyboard()
    
    elif '💧' in text:
        if upgrades['auto_water'] >= 1:
            return "💧 Автополив уже куплен!", get_main_keyboard()
        if user.coins < 1000:
            return f"💰 Не хватает монет! Нужно 1000 монет. У вас {user.coins}", get_main_keyboard()
        
        update_upgrades(user_id, auto_water=1)
        update_user(user_id, coins=user.coins - 1000)
        return f"💧 Автополив куплен! Урожай теперь будет собираться автоматически!", get_main_keyboard()
    
    # ЛОКАЦИИ
    elif text_lower in ['карта', '🗺️ карта', 'локации']:
        msg = get_locations_list_text(user_id)
        return msg, get_locations_keyboard()
    
    elif text_lower.startswith('купить локацию '):
        location_name = text[15:].strip()
        success, msg = buy_location(user_id, location_name)
        if success:
            check_achievements(user_id, vk)
        return msg, get_locations_keyboard()
    
    elif text_lower.startswith('перейти в '):
        location_name = text[10:].strip()
        success, msg = change_location(user_id, location_name)
        return msg, get_locations_keyboard()
    
    elif text_lower in ['моя локация', '📍 моя локация']:
        from locations import LOCATIONS
        current_location = getattr(user, 'current_location', 'Обычная ферма')
        loc_data = LOCATIONS.get(current_location, {})
        harvest_bonus, speed_bonus = get_location_bonus(user_id)
        msg = f"📍 **МОЯ ЛОКАЦИЯ**\n\n"
        msg += f"{loc_data.get('emoji', '🏡')} **{current_location}**\n"
        msg += f"{loc_data.get('description', '')}\n\n"
        msg += f"✨ Текущие бонусы:\n"
        msg += f"   +{harvest_bonus}% к урожаю\n"
        msg += f"   -{abs(speed_bonus)}% времени роста\n\n"
        msg += f"🌱 Доступные культуры в этой локации:\n"
        for crop in get_location_crops(user_id):
            msg += f"   • {crop}\n"
        return msg, get_locations_keyboard()
    
    # ПОСАДКА
    elif text_lower in ['посадить', '🌱 посадить']:
        if user.planted_crop:
            return f"🌱 На поле уже посажено {user.planted_crop}! Сначала соберите урожай.", get_main_keyboard()
        
        # Получаем культуры текущей локации
        allowed_crops = get_location_crops(user_id)
        
        if not allowed_crops:
            return "❌ В этой локации нельзя ничего посадить!", get_main_keyboard()
        
        current_location = getattr(user, 'current_location', 'Обычная ферма')
        
        msg = "🌱 **ВЫБЕРИТЕ КУЛЬТУРУ ДЛЯ ПОСАДКИ**\n\n"
        msg += f"📍 Локация: {current_location}\n"
        msg += f"💰 Ваш баланс: {user.coins}💰\n\n"
        msg += "Доступные культуры:\n"
        
        # Создаем клавиатуру только с доступными культурами
        from vk_api.keyboard import VkKeyboard, VkKeyboardColor
        keyboard = VkKeyboard(one_time=True)
        for crop_name in allowed_crops:
            if crop_name in ALL_CROPS:
                crop = ALL_CROPS[crop_name]
                keyboard.add_button(f"{crop.emoji} {crop.name} ({crop.seed_price}💰)", color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
        keyboard.add_line()
        keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
        
        return msg, keyboard
    
    # СБОР УРОЖАЯ
    elif text_lower in ['собрать', '🌾 собрать']:
        if not user.planted_crop:
            return "🌾 На поле ничего не посажено! Нажмите 'Посадить', чтобы начать.", get_main_keyboard()
        
        crop = None
        for name, c in ALL_CROPS.items():
            if user.planted_crop in name or name == user.planted_crop:
                crop = c
                break
        
        if not crop:
            update_user(user_id, planted_crop=None, planted_at=None)
            return "❌ Произошла ошибка! Попробуйте посадить заново.", get_main_keyboard()
        
        # Получаем бонус от локации
        location_harvest_bonus, location_speed_bonus = get_location_bonus(user_id)
        
        speed_bonus = upgrades['speed_bonus'] + abs(location_speed_bonus)//5
        actual_time = int(crop.grow_seconds * (1 - speed_bonus * 0.05))
        time_passed = time.time() - (user.planted_at or 0)
        
        if time_passed < actual_time:
            remaining = int(actual_time - time_passed)
            minutes = remaining // 60
            seconds = remaining % 60
            if minutes > 0:
                return f"🌱 Урожай ещё не вырос! Осталось {minutes} мин {seconds} сек", get_main_keyboard()
            else:
                return f"🌱 Урожай ещё не вырос! Осталось {seconds} сек", get_main_keyboard()
        
        profit = int(crop.harvest_price * (1 + (upgrades['harvest_bonus'] * 0.05) + (location_harvest_bonus / 100)))
        exp_gain = crop.exp
        new_coins = user.coins + profit
        new_exp = user.exp + exp_gain
        
        level_up = False
        new_level = user.level
        while new_exp >= new_level * 100:
            new_exp -= new_level * 100
            new_level += 1
            level_up = True
        
        update_quest_progress(user_id, 'harvest', 1)
        update_quest_progress(user_id, 'earn', profit)
        
        update_user(user_id, 
                   coins=new_coins, 
                   planted_crop=None, 
                   planted_at=None, 
                   total_harvests=user.total_harvests + 1,
                   exp=new_exp,
                   level=new_level)
        
        reward, unlocked = check_achievements(user_id, vk)
        
        result_msg = f"🌾 Урожай собран! +{profit}💰 +{exp_gain}✨ опыта\n💰 Баланс: {new_coins}"
        
        if level_up:
            result_msg += f"\n\n🏆 **ПОВЫШЕНИЕ УРОВНЯ!**\nТеперь вы {new_level} уровень! 🎉"
        
        if unlocked:
            result_msg += f"\n\n🏅 Получены достижения: {', '.join(unlocked)}! +{reward}💰"
        
        event_message = check_and_trigger_event(user_id)
        if event_message:
            result_msg += f"\n\n{event_message}"
        
        return result_msg, get_main_keyboard()
    
    # ТОП
    elif text_lower in ['топ', '🏆 топ']:
        import sqlite3
        from database import DB_PATH
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, coins, level, nickname, avatar FROM users ORDER BY level DESC, coins DESC LIMIT 10')
        top = cursor.fetchall()
        conn.close()
        
        msg = "🏆 **ТОП ФЕРМЕРОВ** 🏆\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, coins, level, nickname, avatar) in enumerate(top, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            name = nickname if nickname else f"Фермер_{uid}"
            avatar_icon = avatar or "👨‍🌾"
            msg += f"{medal} {avatar_icon} {name} — {level} ур., {coins}💰\n"
        return msg, get_main_keyboard()
    
    # ДОСТИЖЕНИЯ
    elif text_lower in ['достижения', '🏅 достижения']:
        msg = "🏅 **ДОСТИЖЕНИЯ** 🏅\n\n"
        unlocked = user.achievements
        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id in unlocked:
                msg += f"✅ {ach['name']} — {ach['desc']} (+{ach['reward']}💰)\n"
            else:
                msg += f"⬜ {ach['name']} — {ach['desc']}\n"
        msg += f"\n📊 Получено: {len(unlocked)}/{len(ACHIEVEMENTS)}"
        return msg, get_achievements_keyboard()
    
    # КНОПКИ ПОСАДКИ
    else:
        for crop_name, crop in ALL_CROPS.items():
            button_text = f"{crop.emoji} {crop.name} ({crop.seed_price}💰)"
            if text == button_text or text == crop_name or text.lower() == crop.name.lower():
                if user.planted_crop:
                    return f"🌱 На поле уже есть {user.planted_crop}! Сначала собери урожай.", get_main_keyboard()
                if user.coins < crop.seed_price:
                    return f"💰 Не хватает монет! Нужно {crop.seed_price} монет. У вас {user.coins}", get_main_keyboard()
                
                new_coins = user.coins - crop.seed_price
                plant_time = int(time.time())
                
                update_quest_progress(user_id, 'plant', 1)
                
                update_user(user_id, 
                          coins=new_coins, 
                          planted_crop=crop_name, 
                          planted_at=plant_time,
                          total_crops_planted=user.total_crops_planted + 1)
                
                # Получаем бонус от локации
                location_harvest_bonus, location_speed_bonus = get_location_bonus(user_id)
                
                speed_bonus = upgrades['speed_bonus'] + abs(location_speed_bonus)//5
                actual_time = int(crop.grow_seconds * (1 - speed_bonus * 0.05))
                
                notify_when_ready(user_id, crop_name, plant_time + actual_time, vk)
                
                minutes = actual_time // 60
                seconds = actual_time % 60
                time_text = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"
                
                result_msg = f"🌱 {crop.emoji} {crop.name} посажена!\n💰 Осталось: {new_coins} монет\n⏳ Созреет через {time_text}"
                
                event_message = check_and_trigger_event(user_id)
                if event_message:
                    result_msg += f"\n\n{event_message}"
                
                return result_msg, get_main_keyboard()
    
    return None, None

def main():
    """Запуск бота"""
    init_db()
    init_quests_table()
    init_shop_table()
    init_gardening_table()
    init_locations_table()
    
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    print("="*60)
    print("🌈 ВИРТУАЛЬНАЯ ФЕРМА - С ЛОКАЦИЯМИ!")
    print("="*60)
    print("✅ База данных - инициализирована")
    print("✅ Посадка растений - работает")
    print("✅ Сбор урожая - работает")
    print("✅ Животные - работают")
    print("✅ Друзья - работают")
    print("✅ Казино - работает")
    print("✅ Достижения - работают")
    print("✅ Улучшения - работают")
    print("✅ Случайные события - работают")
    print("✅ Квесты - работают")
    print("✅ Магазин предметов - работает")
    print("✅ Садоводство - работает")
    print("✅ Мини-игры - работают")
    print("✅ Статистика - работает")
    print("✅ ЛОКАЦИИ - ДОБАВЛЕНЫ!")
    print("="*60)
    print("Бот запущен и ожидает сообщения...")
    print("="*60)
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text
            
            vk_sessions[user_id] = vk
            
            response, keyboard = handle_message(user_id, text, vk)
            
            if response:
                send_message(vk, user_id, response, keyboard)
                print(f"📨 [{user_id}]: {text[:50]} -> OK")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")