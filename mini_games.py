# mini_games.py
import random
from database import get_user, update_user

def game_dice(user_id: int, bet: int) -> str:
    """Игра в кости"""
    user = get_user(user_id)
    if bet < 10:
        return "❌ Минимальная ставка 10 монет!"
    
    if user.coins < bet:
        return f"💰 Не хватает монет! У вас {user.coins}"
    
    player_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)
    
    if player_roll > bot_roll:
        win = bet * 2
        update_user(user_id, coins=user.coins + win)
        return f"🎲 **ИГРА В КОСТИ** 🎲\n\nВы выбросили: **{player_roll}**\nБот выбросил: **{bot_roll}**\n\n✅ **ВЫ ПОБЕДИЛИ!** +{win}💰\n💰 Баланс: {user.coins + win}"
    elif player_roll < bot_roll:
        update_user(user_id, coins=user.coins - bet)
        return f"🎲 **ИГРА В КОСТИ** 🎲\n\nВы выбросили: **{player_roll}**\nБот выбросил: **{bot_roll}**\n\n❌ **ВЫ ПРОИГРАЛИ!** -{bet}💰\n💰 Баланс: {user.coins - bet}"
    else:
        return f"🎲 **ИГРА В КОСТИ** 🎲\n\nВы выбросили: **{player_roll}**\nБот выбросил: **{bot_roll}**\n\n🤝 **НИЧЬЯ!** Ставка возвращена\n💰 Баланс: {user.coins}"

def game_coinflip(user_id: int, bet: int, choice: str) -> str:
    """Орёл или решка"""
    user = get_user(user_id)
    if bet < 10:
        return "❌ Минимальная ставка 10 монет!"
    
    if user.coins < bet:
        return f"💰 Не хватает монет! У вас {user.coins}"
    
    result = random.choice(['орел', 'решка'])
    choice_lower = choice.lower()
    
    if choice_lower in ['орёл', 'орел', 'орол', 'орел', '1']:
        choice_name = 'орёл'
    elif choice_lower in ['решка', 'рещка', 'решка', '0']:
        choice_name = 'решка'
    else:
        return "❌ Выберите: орёл или решка"
    
    if choice_name == result:
        win = bet * 2
        update_user(user_id, coins=user.coins + win)
        return f"🪙 **ОРЁЛ ИЛИ РЕШКА** 🪙\n\nВыпало: **{result}**\nВы выбрали: {choice_name}\n\n✅ **ВЫ УГАДАЛИ!** +{win}💰\n💰 Баланс: {user.coins + win}"
    else:
        update_user(user_id, coins=user.coins - bet)
        return f"🪙 **ОРЁЛ И РЕШКА** 🪙\n\nВыпало: **{result}**\nВы выбрали: {choice_name}\n\n❌ **ВЫ НЕ УГАДАЛИ!** -{bet}💰\n💰 Баланс: {user.coins - bet}"

def game_blackjack(user_id: int, bet: int) -> str:
    """Простая игра 21 (Blackjack)"""
    user = get_user(user_id)
    if bet < 50:
        return "❌ Минимальная ставка 50 монет!"
    
    if user.coins < bet:
        return f"💰 Не хватает монет! У вас {user.coins}"
    
    # Игрок тянет карты
    player_cards = [random.randint(1, 11), random.randint(1, 11)]
    player_sum = sum(player_cards)
    
    # Бот тянет карты
    bot_cards = [random.randint(1, 11), random.randint(1, 11)]
    bot_sum = sum(bot_cards)
    
    # Бот добирает пока меньше 17
    while bot_sum < 17:
        new_card = random.randint(1, 11)
        bot_cards.append(new_card)
        bot_sum += new_card
    
    msg = f"🃏 **БЛЭКДЖЕК (21)** 🃏\n\n"
    msg += f"Ваши карты: {player_cards} = **{player_sum}**\n"
    msg += f"Карты дилера: [{bot_cards[0]}, ?]\n\n"
    
    if player_sum > 21:
        update_user(user_id, coins=user.coins - bet)
        return msg + f"❌ **ПЕРЕБОР!** Вы проиграли -{bet}💰\n💰 Баланс: {user.coins - bet}"
    
    # Вскрытие
    msg += f"Карты дилера: {bot_cards} = **{bot_sum}**\n\n"
    
    if bot_sum > 21:
        win = bet * 2
        update_user(user_id, coins=user.coins + win)
        return msg + f"✅ **ДИЛЕР ПЕРЕБРАЛ!** +{win}💰\n💰 Баланс: {user.coins + win}"
    elif player_sum > bot_sum:
        win = bet * 2
        update_user(user_id, coins=user.coins + win)
        return msg + f"✅ **ВЫ ВЫИГРАЛИ!** +{win}💰\n💰 Баланс: {user.coins + win}"
    elif player_sum < bot_sum:
        update_user(user_id, coins=user.coins - bet)
        return msg + f"❌ **ДИЛЕР ВЫИГРАЛ!** -{bet}💰\n💰 Баланс: {user.coins - bet}"
    else:
        return msg + f"🤝 **НИЧЬЯ!** Ставка возвращена\n💰 Баланс: {user.coins}"

def get_games_text() -> str:
    """Получить текст с играми"""
    return """🎮 **МИНИ-ИГРЫ** 🎮

🎲 **Кости** - ставка 10+
   Формат: кости <ставка>

🪙 **Орёл/Решка** - ставка 10+
   Формат: орел <ставка>
   Формат: решка <ставка>

🃏 **Блэкджек (21)** - ставка 50+
   Формат: блэкджек <ставка>

💰 Удачи!"""