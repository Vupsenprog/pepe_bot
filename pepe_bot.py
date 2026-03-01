import vk_api
import requests
import time
import os  # ВАЖНО: этот модуль нужен для доступа к переменным окружения
from datetime import datetime, timedelta

# Импортируем безопасные настройки из отдельного файла
from config import *

# --------- ПОЛУЧАЕМ ТОКЕНЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ---------
# Эти значения будут браться из настроек сервера (Timeweb)
VK_TOKEN = os.environ.get('VK_TOKEN')
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
GROUP_DOMAIN = os.environ.get('GROUP_DOMAIN')

# Теперь используем переменные из config.py
processed_posts = set()

def send_telegram(text):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
        if DEBUG:
            print("✅ Уведомление отправлено!")
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")

def cleanup_memory():
    """Очистка старых записей"""
    global processed_posts
    if len(processed_posts) > MAX_POSTS:
        posts_list = list(processed_posts)
        posts_list = posts_list[-MAX_POSTS:]
        processed_posts = set(posts_list)
        if DEBUG:
            print(f"🧹 Очистка памяти: оставили {len(processed_posts)} ID")

def check_vk():
    """Проверка новых постов"""
    global processed_posts
    
    try:
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        posts = vk.wall.get(owner_id=-group_id, count=10, v='5.131')
        
        for post in posts['items']:
            post_id = post['id']
            
            if post_id in processed_posts:
                continue
            
            text = post['text'].lower() if post['text'] else ''
            found = [word for word in KEYWORDS if word.lower() in text]
            
            if found:
                link = f"https://vk.com/wall-{group_id}_{post_id}"
                # Прибавляем 3 часа для Москвы
                moscow_time = datetime.fromtimestamp(post['date']) + timedelta(hours=3)
                time_str = moscow_time.strftime('%d.%m.%Y %H:%M')
                
                msg = f"""🟢 НОВОЕ ОБЪЯВЛЕНИЕ!

Найдено: {', '.join(found)}
Ссылка: {link}
Время: {time_str} (МСК)"""
                
                send_telegram(msg)
            
            processed_posts.add(post_id)
            cleanup_memory()
        
        if DEBUG:
            print(f"📊 В памяти: {len(processed_posts)} ID")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# ---------- ЗАПУСК ----------
print("🚀 Бот запущен!")
print(f"🔍 Ищем слова: {KEYWORDS}")
print(f"⏱️ Интервал: {CHECK_INTERVAL} секунд")
print("📝 Для изменения настроек отредактируйте файл config.py")

while True:
    check_vk()
    time.sleep(CHECK_INTERVAL)

def check_vk():
    global processed_posts
    
    try:
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        posts = vk.wall.get(owner_id=-group_id, count=10, v='5.131')
        
        for post in posts['items']:
            post_id = post['id']
            
            print(f"🔍 Проверяю пост {post_id}")
            
            if post_id in processed_posts:
                print(f"⏭️ Пост {post_id} уже обработан, пропускаю")
                continue
            
            text = post['text'].lower() if post['text'] else ''
            found = [word for word in KEYWORDS if word.lower() in text]
            
            if found:
                print(f"✅ НАШЁЛ в посте {post_id}: {found}")
                link = f"https://vk.com/wall-{group_id}_{post_id}"
                moscow_time = datetime.fromtimestamp(post['date']) + timedelta(hours=3)
                time_str = moscow_time.strftime('%d.%m.%Y %H:%M')
                
                msg = f"""🟢 НОВОЕ ОБЪЯВЛЕНИЕ!

Найдено: {', '.join(found)}
Ссылка: {link}
Время: {time_str} (МСК)"""
                
                send_telegram(msg)
                print(f"✅ Уведомление для поста {post_id} отправлено")
            else:
                print(f"❌ В посте {post_id} ничего не найдено")
            
            # Добавляем пост в обработанные
            processed_posts.add(post_id)
            print(f"➕ Пост {post_id} добавлен в обработанные. Всего в памяти: {len(processed_posts)}")
            cleanup_memory()
        
        print(f"📊 Всего в памяти: {len(processed_posts)} ID")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
