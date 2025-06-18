from flask import Flask, request, jsonify, g
import sqlite3
from datetime import datetime, timedelta
from flask_cors import CORS

DATABASE = 'hotel_search.db'

app = Flask(__name__)
CORS(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/search', methods=['GET'])
def search_hotels():
    area = request.args.get('area')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    rooms = int(request.args.get('rooms', 1))
    guests = int(request.args.get('guests', 1))
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 99999999))
    dinner = request.args.get('dinner', None)

    today = datetime.now().date()
    if not checkin:
        checkin_date = today + timedelta(days=1)
        checkin = checkin_date.strftime('%Y-%m-%d')
    else:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()

    if not checkout:
        checkout_date = today + timedelta(days=7)
        checkout = checkout_date.strftime('%Y-%m-%d')
    else:
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()

    db = get_db()
    params = []
    area_sql = ""
    if area:
        area_sql = "AND hotels.area LIKE ?"
        params.append(f"%{area}%")
    params.extend([min_price, max_price])
    dinner_sql = ""
    if dinner is not None:
        dinner_sql = "AND plans.dinner = ?"
        params.append(1 if dinner.lower() == 'true' else 0)

    sql = f"""
    SELECT hotels.id as hotel_id, hotels.name as hotel_name, hotels.area, plans.id as plan_id, plans.name as plan_name,
           plans.dinner, plans.breakfast, plans.price, rooms.id as room_id, rooms.room_type, rooms.capacity,
           MIN(inventories.available_count) as min_available
    FROM hotels
    JOIN rooms ON hotels.id = rooms.hotel_id
    JOIN plans ON hotels.id = plans.hotel_id
    JOIN inventories ON rooms.id = inventories.room_id AND plans.id = inventories.plan_id
    WHERE 1=1
      {area_sql}
      AND plans.price BETWEEN ? AND ?
      {dinner_sql}
      AND rooms.capacity >= ?
      AND inventories.date >= ? AND inventories.date < ?
    GROUP BY hotels.id, plans.id, rooms.id
    HAVING min_available >= ?
    LIMIT 1000
    """
    params.extend([guests, checkin, checkout, rooms])

    cur = db.execute(sql, params)
    results = []
    seen = set()
    for row in cur.fetchall():
        key = (row["hotel_id"], row["plan_id"])
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "hotel_id": row["hotel_id"],
            "hotel_name": row["hotel_name"],
            "area": row["area"],
            "plan_id": row["plan_id"],
            "plan_name": row["plan_name"],
            "dinner": bool(row["dinner"]),
            "breakfast": bool(row["breakfast"]),
            "price": row["price"],
            "room_id": row["room_id"],
            "room_type": row["room_type"],
            "capacity": row["capacity"],
            "min_available": row["min_available"]
        })
        if len(results) >= 100:
            break  # 最大100件まで返す

    return jsonify(results)

@app.route('/api/photos')
def get_photos():
    hotel_photos = [f"/hotel_photos/hotel{i}.jpg" for i in range(1, 11)]
    room_photos = [f"/room_photos/room{i}.jpg" for i in range(1, 11)]
    return jsonify({
        "hotel_photos": hotel_photos,
        "room_photos": room_photos
    })

if __name__ == '__main__':
    app.run(debug=True)
