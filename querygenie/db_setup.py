"""
Creates a realistic sample SQLite database (store.db) so the app works
out of the box on any laptop — no external database server needed.

Run once:  python db_setup.py
"""

import os
import sqlite3
import random
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

CUSTOMERS = [
    ("Aarav Sharma", "Mumbai"),
    ("Diya Patel", "Ahmedabad"),
    ("Vivaan Reddy", "Hyderabad"),
    ("Ananya Nair", "Kochi"),
    ("Ishaan Gupta", "Delhi"),
    ("Meera Iyer", "Chennai"),
    ("Kabir Singh", "Kolkata"),
    ("Riya Das", "Bengaluru"),
]

PRODUCTS = [
    ("Wireless Mouse", "Electronics", 799),
    ("Mechanical Keyboard", "Electronics", 3499),
    ("USB-C Hub", "Electronics", 1999),
    ("Notebook A5", "Stationery", 149),
    ("Gel Pen Pack", "Stationery", 99),
    ("Desk Lamp", "Home", 1299),
    ("Coffee Mug", "Home", 349),
    ("Backpack", "Accessories", 2499),
    ("Water Bottle", "Accessories", 599),
    ("Headphones", "Electronics", 4999),
]


def build():
    """
    Create the sample database if needed and seed it once.

    This is IDEMPOTENT: it is safe to call on every app start. It uses
    'CREATE TABLE IF NOT EXISTS' and only inserts data when the tables are
    empty, so it never crashes on re-runs (important on hosted platforms
    like Streamlit Cloud where the script runs many times).
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            city    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products (
            id       INTEGER PRIMARY KEY,
            name     TEXT NOT NULL,
            category TEXT NOT NULL,
            price    REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL,
            product_id   INTEGER NOT NULL,
            quantity     INTEGER NOT NULL,
            order_date   TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id)  REFERENCES products(id)
        );
        """
    )

    # Only seed if the database is empty.
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO customers (name, city) VALUES (?, ?)", CUSTOMERS)
        cur.executemany(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)", PRODUCTS
        )

        random.seed(42)
        start = date.today() - timedelta(days=180)
        orders = []
        for _ in range(200):
            customer_id = random.randint(1, len(CUSTOMERS))
            product_id = random.randint(1, len(PRODUCTS))
            quantity = random.randint(1, 5)
            order_date = (start + timedelta(days=random.randint(0, 180))).isoformat()
            orders.append((customer_id, product_id, quantity, order_date))

        cur.executemany(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) "
            "VALUES (?, ?, ?, ?)",
            orders,
        )
        conn.commit()
        print(f"Seeded {DB_PATH} with {len(CUSTOMERS)} customers, "
              f"{len(PRODUCTS)} products and {len(orders)} orders.")
    else:
        print(f"{DB_PATH} already contains data - nothing to seed.")

    conn.close()


if __name__ == "__main__":
    build()
