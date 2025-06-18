-- ホテル情報
CREATE TABLE hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    area TEXT NOT NULL,
    address TEXT,
    latitude REAL,
    longitude REAL
);

-- 部屋情報
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    room_type TEXT,
    capacity INTEGER,
    FOREIGN KEY(hotel_id) REFERENCES hotels(id)
);

-- プラン情報
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    name TEXT,
    dinner BOOLEAN,
    breakfast BOOLEAN,
    price INTEGER,
    FOREIGN KEY(hotel_id) REFERENCES hotels(id)
);

-- 在庫情報
CREATE TABLE inventories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    date TEXT NOT NULL, -- YYYY-MM-DD
    available_count INTEGER,
    price INTEGER,
    FOREIGN KEY(room_id) REFERENCES rooms(id),
    FOREIGN KEY(plan_id) REFERENCES plans(id)
);

-- オプション情報（例：夕食、温泉など）
CREATE TABLE options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    option_name TEXT,
    FOREIGN KEY(plan_id) REFERENCES plans(id)
);
