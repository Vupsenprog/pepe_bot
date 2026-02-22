import vk_api
import requests
import time
import os
from datetime import datetime

# ---------- НАСТРОЙКИ ----------
VK_TOKEN = os.environ.get('VK_TOKEN')
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
GROUP_DOMAIN = os.environ.get('GROUP_DOMAIN')

# Слова для поиска
KEYWORDS = ['рогатка', 'ceratophrys', 'cornuta', 'корнута', 'рогатки', 'амазонская', 'итания', 'итанния']

# ---------- ВАЖНО! ОГРАНИЧЕНИЕ ПАМЯТИ ----------
# Храним ТОЛЬКО последние 50 ID постов (это 0.001% от 800 МБ)
MAX_POSTS = 50
processed_posts = set()

print(f"🚀 Бот запущен! Будет храниться максимум {MAX_POSTS} ID постов")

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
        print("✅ Уведомление отправлено!")
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")

def cleanup_memory():
    """Очистка старых записей для экономии памяти"""
    global processed_posts
    
    # Считаем сколько сейчас хранится ID
    current_size = len(processed_posts)
    
    # Если превысили лимит - удаляем лишнее
    if current_size > MAX_POSTS:
        # Превращаем множество в список, берем последние MAX_POSTS
        # и превращаем обратно во множество
        posts_list = list(processed_posts)
        # Берем последние MAX_POSTS штук
        posts_list = posts_list[-MAX_POSTS:]
        processed_posts = set(posts_list)
        
        print(f"🧹 Очистка памяти: было {current_size} ID, оставили {len(processed_posts)}")

def check_vk():
    """Проверка новых постов ВК"""
    global processed_posts
    
    try:
        # Подключаемся к ВК
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        
        # Получаем информацию о группе
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        # Получаем последние 10 постов
        posts = vk.wall.get(owner_id=-group_id, count=10, v='5.131')
        
        for post in posts['items']:
            post_id = post['id']
            
            # Пропускаем уже проверенные посты
            if post_id in processed_posts:
                continue
            
            # Проверяем текст
            text = post['text'].lower() if post['text'] else ''
            found = []
            
            for word in KEYWORDS:
                if word.lower() in text:
                    found.append(word)
            
            # Если нашли слова - отправляем уведомление
            if found:
                link = f"https://vk.com/wall-{group_id}_{post_id}"
                time_str = datetime.fromtimestamp(post['date']).strftime('%d.%m.%Y %H:%M')
                
                msg = f"""🔔 НОВОЕ ОБЪЯВЛЕНИЕ!

Найдено: {', '.join(found)}
Ссылка: {link}
Время: {time_str}"""
                
                send_telegram(msg)
            
            # Запоминаем пост (ДОБАВЛЯЕМ В set)
            processed_posts.add(post_id)
            
            # ---------- ВАЖНО! ОЧИСТКА ПОСЛЕ КАЖДОГО ПОСТА ----------
            cleanup_memory()
        
        # Показываем сколько сейчас хранится ID (для отладки)
        print(f"📊 Сейчас в памяти: {len(processed_posts)} ID постов")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке ВК: {e}")

# ---------- ОСНОВНОЙ ЦИКЛ ----------
print(f"🔍 Ищем слова: {KEYWORDS}")
print(f"⏱️  Интервал проверки: 6000 секунд (1 час 40 минут)")

check_counter = 0

while True:
    check_vk()
    
    # Счетчик для периодической очистки
    check_counter += 1
    
    # Каждые 10 проверок делаем дополнительную очистку
    if check_counter % 10 == 0:
        cleanup_memory()
        print(f"🔄 Плановое обслуживание памяти")
        check_counter = 0
    
    # Ждем перед следующей проверкой
    time.sleep(3600)  # 3600 секунд = 1 час 00 минут
