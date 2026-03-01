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
    """Проверка новых постов с подробной отладкой"""
    global processed_posts
    
    try:
        print("\n" + "="*50)
        print("🔄 НАЧАЛО ПРОВЕРКИ")
        print(f"📊 ТЕКУЩИЙ РАЗМЕР processed_posts: {len(processed_posts)}")
        print(f"📋 ПОСЛЕДНИЕ 10 ID В ПАМЯТИ: {sorted(list(processed_posts))[-10:] if processed_posts else '[]'}")
        
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        posts = vk.wall.get(owner_id=-group_id, count=10, v='5.131')
        print(f"📥 ПОЛУЧЕНО {len(posts['items'])} ПОСТОВ ИЗ ВК")
        
        for i, post in enumerate(posts['items']):
            post_id = post['id']
            print(f"\n--- ПОСТ #{i+1} (ID: {post_id}) ---")
            
            # Проверяем, есть ли пост в памяти
            in_memory = post_id in processed_posts
            print(f"🔍 Пост {post_id} уже в processed_posts? {in_memory}")
            
            # Получаем текст поста
            text = post['text'].lower() if post['text'] else ''
            print(f"📝 Текст поста (первые 100 символов): {text[:100]}...")
            
            # Ищем ключевые слова
            found = [word for word in KEYWORDS if word.lower() in text]
            print(f"🔎 Найденные слова: {found if found else 'НЕТ'}")
            
            # Пропускаем, если пост уже обработан
            if in_memory:
                if found:
                    print(f"⚠️⚠️⚠️ ВНИМАНИЕ! Пост {post_id} УЖЕ В ПАМЯТИ, но содержит ключевые слова!")
                    print(f"⚠️ Это объясняет повторные уведомления!")
                else:
                    print(f"⏭️ Пост {post_id} уже обработан (нет ключевых слов)")
                continue
            
            # Если нашли слова - отправляем уведомление
            if found:
                print(f"✅✅✅ НОВЫЙ ПОСТ {post_id} с ключевыми словами! ОТПРАВЛЯЮ УВЕДОМЛЕНИЕ")
                
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
                print(f"❌ В посте {post_id} ключевых слов не найдено")
            
            # Добавляем пост в обработанные (ВАЖНО: добавляем ВСЕГДА!)
            processed_posts.add(post_id)
            print(f"➕ Пост {post_id} ДОБАВЛЕН в processed_posts")
            print(f"📊 Размер processed_posts после добавления: {len(processed_posts)}")
            
            # Вызываем очистку памяти
            old_size = len(processed_posts)
            cleanup_memory()
            new_size = len(processed_posts)
            if old_size != new_size:
                print(f"🧹 cleanup_memory сработала: было {old_size}, стало {new_size}")
        
        # Итог проверки
        print("\n📊 ИТОГ ПРОВЕРКИ:")
        print(f"📊 Всего в памяти: {len(processed_posts)} ID")
        print(f"📋 Последние 10 ID: {sorted(list(processed_posts))[-10:] if processed_posts else '[]'}")
        print("="*50 + "\n")
            
    except Exception as e:
        print(f"❌ ОШИБКА В check_vk: {e}")
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

