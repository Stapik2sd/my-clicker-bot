# keyboards.py
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from game_data import CROPS, SKINS, ANIMALS

def get_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('🌾 Ферма', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('💰 Баланс', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('🌱 Посадить', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('🌾 Собрать', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('🗺️ Карта', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('📦 Инвентарь', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('🏆 Топ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎁 Бонус', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('🏪 Магазин', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('🛍️ Предметы', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('📋 Квесты', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('👤 Профиль', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('👥 Друзья', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🏅 Достижения', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('🐔 Животные', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎰 Казино', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('🌻 Сад', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎮 Игры', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('🌤️ Прогноз погоды', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('📊 Моя статистика', color=VkKeyboardColor.PRIMARY)
    return keyboard

def get_plant_keyboard():
    keyboard = VkKeyboard(one_time=True)
    crops_list = list(CROPS.items())
    for i in range(0, len(crops_list), 2):
        if i < len(crops_list):
            crop_name, crop = crops_list[i]
            keyboard.add_button(f"{crop.emoji} {crop.name} ({crop.seed_price}💰)", color=VkKeyboardColor.PRIMARY)
        if i + 1 < len(crops_list):
            crop_name, crop = crops_list[i + 1]
            keyboard.add_button(f"{crop.emoji} {crop.name} ({crop.seed_price}💰)", color=VkKeyboardColor.PRIMARY)
        if i + 1 < len(crops_list):
            keyboard.add_line()
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_animals_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('🐔 Купить курицу (100💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🐮 Купить корову (500💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('🐑 Купить овцу (300💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🐷 Купить свинью (400💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('🐝 Купить пчелу (150💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🦆 Купить утку (80💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('💰 Собрать доход', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_profile_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('✏️ Сменить ник (100💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎭 Сменить скин', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_skins_keyboard():
    keyboard = VkKeyboard(one_time=False)
    for skin_name, skin_data in SKINS.items():
        price_text = f" ({skin_data['price']}💰)" if skin_data['price'] > 0 else " (бесплатно)"
        keyboard.add_button(f"{skin_data['emoji']} {skin_name}{price_text}", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
    keyboard.add_button('◀ Назад', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_friends_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('➕ Добавить друга', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('📩 Заявки', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('👥 Мои друзья', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_upgrade_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('🔨 Урожайность (500💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('⚡ Скорость (300💰)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('💧 Автополив (1000💰)', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_achievements_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_casino_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('🎲 50', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎲 100', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎲 200', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('🎲 500', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('🎲 1000', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('📊 Статистика', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_locations_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('🗺️ Список локаций', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('📍 Моя локация', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('◀ На главную', color=VkKeyboardColor.SECONDARY)
    return keyboard