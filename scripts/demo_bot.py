import requests
import os
import json
import time
import random
from dotenv import load_dotenv

load_dotenv()

SUBDOMAIN = os.getenv("RETAILCRM_SUBDOMAIN")
API_KEY = os.getenv("RETAILCRM_API_KEY")

def create_real_order(first_name, last_name, price, city):
    url = f"https://{SUBDOMAIN}.retailcrm.ru/api/v5/orders/create"
    
    # Случайный способ оплаты для разнообразия графиков
    payment_type = random.choice(["cash", "bank-card", "kaspi-transfer"])
    
    order_data = {
        "firstName": first_name,
        "lastName": last_name,
        "phone": "+7" + str(int(time.time()))[-10:],
        "status": "new",
        "delivery": {"address": {"city": city}},
        "items": [
            {
                "initialPrice": price,
                "quantity": 1,
                "productName": "VIP Товар (Демо-тест)",
            }
        ],
        "payments": [
            {
                "type": payment_type,
                "amount": price,
                "status": "not-paid" if payment_type == "cash" else "paid"
            }
        ],
        "customerComment": "Демо-заказ с типом оплаты"
    }

    data = {"site": SUBDOMAIN, "order": json.dumps(order_data)}
    params = {"apiKey": API_KEY}
    
    try:
        response = requests.post(url, params=params, data=data, timeout=10)
        res_json = response.json()
        if res_json.get("success"):
            print(f"✅ #{res_json['order']['number']} — {price} ₸ (Оплата: {payment_type})")
            return True
        return False
    except:
        return False

demo_data = [
    ("Алексей", "Иванов", 45000, "Алматы"),
    ("Мариам", "Тестова", 39000, "Астана"),
    ("Джон", "Доу", 48000, "Костанай"),
    ("Анна", "Седокова", 42000, "Шымкент"),
    ("Павел", "Воля", 44000, "Алматы"),
    ("Светлана", "Лобода", 89000, "Астана"),
    ("Григорий", "Лепс", 115000, "Алматы"),
    ("Михаил", "Галустян", 76000, "Караганда"),
    ("Сергей", "Жуков", 150000, "Актау"),
    ("Илья", "Прусикин", 130000, "Алматы")
]

print("--- Запуск демо-генерации С ТИПАМИ ОПЛАТЫ ---")
for fn, ln, ts, city in demo_data:
    create_real_order(fn, ln, ts, city)
    time.sleep(10)
print("\nГотово!")
