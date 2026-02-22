import time
import os

print("🚀 ТЕСТОВЫЙ БОТ ЗАПУЩЕН")
print(f"VK_TOKEN задан: {'ДА' if os.environ.get('VK_TOKEN') else 'НЕТ'}")
print(f"TG_TOKEN задан: {'ДА' if os.environ.get('TG_TOKEN') else 'НЕТ'}")
print(f"TG_CHAT_ID задан: {'ДА' if os.environ.get('TG_CHAT_ID') else 'НЕТ'}")
print(f"GROUP_DOMAIN задан: {'ДА' if os.environ.get('GROUP_DOMAIN') else 'НЕТ'}")

counter = 0
while True:
    counter += 1
    print(f"🔄 Проверка #{counter} в {time.strftime('%H:%M:%S')}")
    time.sleep(30)  # Каждые 30 секунд
