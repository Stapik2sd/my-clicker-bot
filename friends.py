# friends.py
import random
import time
from database import get_user, get_friends, get_friend_requests, add_friend_request, accept_friend_request, reject_friend_request
from utils import vk_sessions

def get_friends_list_text(user_id: int) -> str:
    """Получить текст со списком друзей"""
    friends = get_friends(user_id)
    if not friends:
        return "👥 У вас пока нет друзей! Добавьте кого-нибудь."
    
    msg = "👥 **МОИ ДРУЗЬЯ:**\n\n"
    for fid in friends[:20]:
        friend = get_user(fid)
        msg += f"• {friend.avatar} {friend.nickname} (ур. {friend.level}, {friend.coins}💰)\n"
    if len(friends) > 20:
        msg += f"\n... и ещё {len(friends) - 20} друзей"
    return msg

def get_friend_requests_text(user_id: int) -> str:
    """Получить текст со списком заявок"""
    requests = get_friend_requests(user_id)
    if not requests:
        return "📩 Нет новых заявок в друзья!"
    
    msg = "📩 **НОВЫЕ ЗАЯВКИ:**\n\n"
    for from_id in requests:
        user = get_user(from_id)
        msg += f"• {user.avatar} {user.nickname} (ID: {from_id})\n"
        msg += f"   → /принять {from_id} | /отклонить {from_id}\n\n"
    return msg

def send_friend_request(user_id: int, friend_id: int, vk=None) -> tuple:
    """Отправить заявку в друзья"""
    if user_id == friend_id:
        return False, "❌ Нельзя добавить самого себя!"
    
    # Проверяем, не друзья ли уже
    friends = get_friends(user_id)
    if friend_id in friends:
        return False, "❌ Вы уже друзья!"
    
    # Отправляем заявку
    if add_friend_request(user_id, friend_id):
        # Отправляем уведомление, если есть vk и пользователь в сессиях
        if vk and friend_id in vk_sessions:
            try:
                vk.messages.send(
                    user_id=friend_id,
                    message=f"🌟 Пользователь отправил вам заявку в друзья!\n\nЧтобы принять, напишите: /принять {user_id}",
                    random_id=random.randint(1, 2**31)
                )
            except:
                pass
        return True, f"✅ Заявка отправлена пользователю с ID {friend_id}!"
    else:
        return False, "❌ Заявка уже отправлена!"

def accept_request(user_id: int, from_id: int, vk=None) -> tuple:
    """Принять заявку в друзья"""
    if accept_friend_request(user_id, from_id):
        # Отправляем уведомление
        if vk and from_id in vk_sessions:
            try:
                vk.messages.send(
                    user_id=from_id,
                    message=f"🎉 Пользователь принял вашу заявку в друзья!",
                    random_id=random.randint(1, 2**31)
                )
            except:
                pass
        return True, "✅ Друг добавлен!"
    else:
        return False, "❌ Заявка не найдена!"

def reject_request(user_id: int, from_id: int) -> tuple:
    """Отклонить заявку"""
    reject_friend_request(user_id, from_id)
    return True, "❌ Заявка отклонена!"

def get_friends_keyboard_text() -> str:
    """Текст для меню друзей"""
    return "👥 **ДРУЗЬЯ**\n\n➕ Добавить друга: друг <id>\n📩 Заявки: заявки\n👥 Мои друзья: мои друзья"