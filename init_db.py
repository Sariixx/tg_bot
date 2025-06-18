import sqlite3
import os

DB_PATH = "rental.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS orders')
    c.execute('DROP TABLE IF EXISTS vehicles')

    c.execute('''
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            model TEXT NOT NULL,
            power INTEGER NOT NULL,
            range_km INTEGER NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 5,
            max_quantity INTEGER NOT NULL DEFAULT 5
        )
    ''')

    c.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            order_code TEXT UNIQUE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')

    # Реальні (або більш правдоподібні) комерційні моделі
    vehicles = [
        # electric bikes
        ('electric_bike', 'Specialized Turbo Vado 4.0', 250, 40, 300, 5, 5),
        ('electric_bike', 'Giant Explore E+', 500, 120, 450, 5, 5),

        # electric scooters
        ('electric_scooter', 'Xiaomi Mi Electric Scooter 3', 300, 30, 150, 5, 5),
        ('electric_scooter', 'Segway Ninebot ZT3 Pro E', 550, 65, 200, 5, 5)
    ]
    c.executemany(
        'INSERT INTO vehicles (type, model, power, range_km, price, quantity, max_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)',
        vehicles
    )

    c.execute("CREATE INDEX IF NOT EXISTS idx_orders_active   ON orders(active)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_orders_vehicle  ON orders(vehicle_id)")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("База даних успішно ініціалізована!")