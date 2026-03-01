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
    """Проверка новых постов — ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    global processed_posts
    
    try:
        print("\n" + "🔴"*30)
        print(f"🔄 НАЧАЛО ПРОВЕРКИ в {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 В ПАМЯТИ СЕЙЧАС: {len(processed_posts)} ID")
        
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        posts = vk.wall.get(owner_id=-group_id, count=10, v='5.131')
        print(f"📥 Получено {len(posts['items'])} постов")
        
        for post in posts['items']:
            post_id = post['id']
            
            print(f"\n--- ПОСТ ID: {post_id} ---")
            
            # 1. СНАЧАЛА ПРОВЕРЯЕМ, есть ли пост в памяти
            if post_id in processed_posts:
                print(f"⏭️ Пост {post_id} уже обработан, пропускаем")
                continue  # ВАЖНО: сразу переходим к следующему посту
            
            # 2. ЕСЛИ ПОСТА НЕТ В ПАМЯТИ, тогда проверяем текст
            text = post['text'].lower() if post['text'] else ''
            found = [word for word in KEYWORDS if word.lower() in text]
            
            # 3. Если нашли слова — отправляем уведомление
            if found:
                print(f"✅ НАЙДЕН НОВЫЙ ПОСТ {post_id} со словами: {found}")
                
                link = f"https://vk.com/wall-{group_id}_{post_id}"
                moscow_time = datetime.fromtimestamp(post['date']) + timedelta(hours=3)
                time_str = moscow_time.strftime('%d.%m.%Y %H:%M')
                
                msg = f"""🟢 НОВОЕ ОБЪЯВЛЕНИЕ!

Найдено: {', '.join(found)}
Ссылка: {link}
Время: {time_str} (МСК)"""
                
                send_telegram(msg)
                print(f"✅ Уведомление отправлено для поста {post_id}")
            else:
                print(f"❌ В посте {post_id} ключевых слов не найдено")
            
            # 4. В ЛЮБОМ СЛУЧАЕ добавляем пост в обработанные
            processed_posts.add(post_id)
            print(f"➕ Пост {post_id} добавлен в обработанные. Теперь в памяти: {len(processed_posts)}")
            
            # 5. Очистка памяти
            cleanup_memory()
        
        print(f"📊 ИТОГ: в памяти {len(processed_posts)} ID")
        print("🔴"*30 + "\n")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        

# ---------- ЗАПУСК ----------
print("🚀 Бот запущен!")
print(f"🔍 Ищем слова: {KEYWORDS}")
print(f"⏱️ Интервал: {CHECK_INTERVAL} секунд")
print("📝 Для изменения настроек отредактируйте файл config.py")

while True:
    check_vk()
    time.sleep(CHECK_INTERVAL)

