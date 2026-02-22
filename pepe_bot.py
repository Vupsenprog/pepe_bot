import vk_api
import requests
import time
from datetime import datetime

# Импортируем ВСЕ настройки из отдельного файла
from config import *

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
                time_str = datetime.fromtimestamp(post['date']).strftime('%d.%m.%Y %H:%M')
                
                msg = f"""🔔 НОВОЕ ОБЪЯВЛЕНИЕ!

Найдено: {', '.join(found)}
Ссылка: {link}
Время: {time_str}"""
                
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
