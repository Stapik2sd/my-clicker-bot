# animals.py
import time
from database import get_user, update_user, get_animals, add_animal, update_animal_collect
from game_data import ANIMALS

def get_animal_shop_text() -> str:
    """Текст магазина животных"""
    msg = "🐔 **МАГАЗИН ЖИВОТНЫХ** 🐮\n\n"
    for animal_type, animal in ANIMALS.items():
        msg += f"{animal.emoji} {animal.name} — {animal.price}💰 (доход: {animal.income}💰 каждые {animal.interval} сек)\n"
        msg += f"   Максимум: {animal.max_count} шт.\n\n"
    return msg

def buy_animal(user_id: int, animal_type: str):
    """Купить животное"""
    if animal_type not in ANIMALS:
        return False, "Такого животного нет!"
    
    animal = ANIMALS[animal_type]
    user = get_user(user_id)
    animals = get_animals(user_id)
    
    current_count = animals.get(animal_type, {}).get('count', 0)
    if current_count >= animal.max_count:
        return False, f"❌ Максимум {animal.max_count} {animal.name}!"
    
    if user.coins < animal.price:
        return False, f"💰 Не хватает! Нужно {animal.price} монет. У вас {user.coins}"
    
    # Покупаем
    update_user(user_id, coins=user.coins - animal.price)
    add_animal(user_id, animal_type)
    
    return True, f"✅ {animal.emoji} {animal.name} куплена! -{animal.price}💰\n📊 Теперь у вас {current_count + 1} шт."

def collect_animal_income(user_id: int):
    """Собрать доход с животных"""
    animals = get_animals(user_id)
    if not animals:
        return 0, []
    
    total_income = 0
    now = int(time.time())
    collected = []
    
    for animal_type, data in animals.items():
        if animal_type not in ANIMALS:
            continue
        
        animal = ANIMALS[animal_type]
        count = data['count']
        last = data['last_collect']
        
        if count > 0:
            elapsed = now - last
            intervals = elapsed // animal.interval
            
            if intervals > 0:
                income = intervals * count * animal.income
                total_income += income
                collected.append(f"{animal.emoji} {animal.name}: +{income}💰")
                
                new_last = last + (intervals * animal.interval)
                update_animal_collect(user_id, animal_type, new_last)
    
    if total_income > 0:
        user = get_user(user_id)
        update_user(user_id, coins=user.coins + total_income)
    
    return total_income, collected

def get_my_animals_text(user_id: int) -> str:
    """Текст с животными пользователя"""
    animals = get_animals(user_id)
    if not animals:
        return get_animal_shop_text()
    
    msg = "🐔 **ТВОИ ЖИВОТНЫЕ** 🐮\n\n"
    total_ready = 0
    
    for animal_type, data in animals.items():
        if animal_type in ANIMALS:
            animal = ANIMALS[animal_type]
            count = data['count']
            last = data['last_collect']
            now = int(time.time())
            elapsed = now - last
            ready_count = elapsed // animal.interval
            ready_income = ready_count * count * animal.income
            total_ready += ready_income
            
            msg += f"{animal.emoji} {animal.name}: {count} шт."
            if ready_income > 0:
                msg += f" → +{ready_income}💰 готово"
            msg += "\n"
    
    if total_ready > 0:
        msg += f"\n💰 Готово к сбору: {total_ready}💰"
    return msg