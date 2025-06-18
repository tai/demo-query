import random
import sqlite3
from datetime import datetime, timedelta

# パラメータ
num_hotels = 5000000
min_rooms_per_hotel = 10
max_rooms_per_hotel = 50
min_room_types = 1
max_room_types = 5
num_plans = 10
num_days = 50

# サンプル名リスト
area_names = [
    "Paris",
    "London",
    "New York",
    "Tokyo",
    "Rome",
    "Barcelona",
    "Istanbul",
    "Dubai",
    "Bangkok",
    "Singapore",
    "Hong Kong",
    "Sydney",
    "Los Angeles",
    "San Francisco",
    "Rio de Janeiro",
    "Cape Town",
    "Cairo",
    "Moscow",
    "Berlin",
    "Toronto",
    "Beijing",
    "Shanghai",
    "Seoul",
    "Delhi",
    "Mumbai",
    "Kuala Lumpur",
    "Bali",
    "Phuket",
    "Maldives",
    "Santorini",
    "Venice",
    "Florence",
    "Prague",
    "Vienna",
    "Budapest",
    "Amsterdam",
    "Lisbon",
    "Madrid",
    "Dublin",
    "Edinburgh",
    "Athens",
    "Dubrovnik",
    "Reykjavik",
    "Helsinki",
    "Stockholm",
    "Copenhagen",
    "Oslo",
    "Zurich",
    "Geneva",
    "Nice",
    "Monaco",
    "Marseille",
    "Munich",
    "Frankfurt",
    "Warsaw",
    "Krakow",
    "Bucharest",
    "Sofia",
    "Hanoi",
    "Yangon",
    "Jakarta",
    "Manila",
    "Cebu",
    "Queenstown"
]

room_type_names = [f'Type{i}' for i in range(1, max_room_types+1)]
plan_names = [f'Plan{i}' for i in range(1, num_plans+1)]

conn = sqlite3.connect('hotel_search.db')
cur = conn.cursor()

# 既存データ削除
cur.execute('DELETE FROM inventories')
cur.execute('DELETE FROM options')
cur.execute('DELETE FROM plans')
cur.execute('DELETE FROM rooms')
cur.execute('DELETE FROM hotels')
conn.commit()

# ホテル投入
hotel_ids = []
for i in range(num_hotels):
    name = f'Hotel{i+1}'
    area = random.choice(area_names)
    address = f'{area} Address {i+1}'
    latitude = 35.0 + (i % 100) * 0.01
    longitude = 135.0 + (i % 100) * 0.01
    cur.execute('INSERT INTO hotels (name, area, address, latitude, longitude) VALUES (?, ?, ?, ?, ?)',
                (name, area, address, latitude, longitude))
    hotel_ids.append(cur.lastrowid)

# 部屋投入
room_ids = []
hotel_room_map = {}
for hotel_id in hotel_ids:
    num_room_types = random.randint(min_room_types, max_room_types)
    num_rooms = random.randint(min_rooms_per_hotel, max_rooms_per_hotel)
    rooms_per_type = [num_rooms // num_room_types] * num_room_types
    for j in range(num_rooms % num_room_types):
        rooms_per_type[j] += 1
    hotel_room_map[hotel_id] = []
    for rt_index in range(num_room_types):
        room_type = room_type_names[rt_index]
        capacity = random.randint(1, 4)
        for _ in range(rooms_per_type[rt_index]):
            cur.execute('INSERT INTO rooms (hotel_id, room_type, capacity) VALUES (?, ?, ?)',
                        (hotel_id, room_type, capacity))
            room_id = cur.lastrowid
            room_ids.append(room_id)
            hotel_room_map[hotel_id].append(room_id)

# プラン投入
plan_ids = []
hotel_plan_map = {}
for hotel_id in hotel_ids:
    hotel_plan_map[hotel_id] = []
    for plan_name in plan_names:
        dinner = random.choice([True, False])
        breakfast = random.choice([True, False])
        price = random.randint(8000, 30000)
        cur.execute('INSERT INTO plans (hotel_id, name, dinner, breakfast, price) VALUES (?, ?, ?, ?, ?)',
                    (hotel_id, plan_name, dinner, breakfast, price))
        plan_id = cur.lastrowid
        plan_ids.append(plan_id)
        hotel_plan_map[hotel_id].append(plan_id)

# オプション投入
for plan_id in plan_ids:
    options = []
    if random.choice([True, False]):
        options.append('Free WiFi')
    if random.choice([True, False]):
        options.append('Hot Spring')
    for option in options:
        cur.execute('INSERT INTO options (plan_id, option_name) VALUES (?, ?)', (plan_id, option))

# 在庫投入（最初の10ホテルだけサンプルで1年分）
start_date = datetime.now().date()
sample_hotel_ids = hotel_ids[:10]
for hotel_id in sample_hotel_ids:
    rooms_for_hotel = hotel_room_map.get(hotel_id, [])
    plans_for_hotel = hotel_plan_map.get(hotel_id, [])
    for room_id in rooms_for_hotel:
        for plan_id in plans_for_hotel:
            for day_offset in range(num_days):
                date = start_date + timedelta(days=day_offset)
                available_count = random.randint(0, 5)
                price = random.randint(8000, 30000)
                cur.execute('INSERT INTO inventories (room_id, plan_id, date, available_count, price) VALUES (?, ?, ?, ?, ?)',
                            (room_id, plan_id, date.isoformat(), available_count, price))

conn.commit()
conn.close()

print('Sample data generated: 5000 hotels, rooms, plans, and 1 year inventory for 10 hotels.')
