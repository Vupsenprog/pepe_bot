import vk_api
import requests
import time
import os
from datetime import datetime

# Токены берутся из переменных окружения на Render
VK_TOKEN = os.environ.get('VK_TOKEN')
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
GROUP_DOMAIN = os.environ.get('GROUP_DOMAIN')

# Слова для поиска
KEYWORDS = ['рогатка', 'ceratophrys', 'cornuta', 'корнута', 'рогатки', 'амазонская', 'итания', 'итанния']

# Храним ID постов, которые уже проверили
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
        print("✅ Уведомление отправлено!")
    except:
        print("❌ Ошибка отправки в Telegram")

def check_vk():
    """Проверка новых постов ВК"""
    global processed_posts
    
    try:
        # Подключаемся к ВК
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        
        # Получаем информацию о группе
        group = vk.groups.getById(group_id=GROUP_DOMAIN)[0]
        group_id = group['id']
        
        # Получаем последние 5 постов
        posts = vk.wall.get(owner_id=-group_id, count=5, v='5.131')
        
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
            
            # Запоминаем пост
            processed_posts.add(post_id)
            
        # Оставляем только последние 100 постов в памяти
        if len(processed_posts) > 100:
            processed_posts = set(list(processed_posts)[-100:])
            
    except Exception as e:
        print(f"Ошибка: {e}")

print("🚀 Бот запущен!")
print(f"🔍 Ищем слова: {KEYWORDS}")

# Бесконечный цикл проверки
while True:
    check_vk()
    time.sleep(30)  # Проверка каждые 30 секунд
