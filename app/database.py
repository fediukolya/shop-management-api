import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не знайдено у файлі .env")


def get_connection():
    """Створює підключення до PostgreSQL."""
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )


def init_db():
    """Створює таблиці бази даних магазину."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                sku VARCHAR(50) NOT NULL UNIQUE,
                category_id INTEGER NOT NULL
                    REFERENCES categories(id),
                price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
            );

            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                phone VARCHAR(30)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL
                    REFERENCES customers(id),
                status VARCHAR(30) NOT NULL DEFAULT 'new'
                    CHECK (
                        status IN (
                            'new',
                            'processing',
                            'completed',
                            'cancelled'
                        )
                    ),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL
                    REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL
                    REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price NUMERIC(10, 2) NOT NULL
                    CHECK (unit_price >= 0),
                UNIQUE (order_id, product_id)
            );

            CREATE INDEX IF NOT EXISTS idx_products_category
                ON products(category_id);

            CREATE INDEX IF NOT EXISTS idx_orders_customer
                ON orders(customer_id);

            CREATE INDEX IF NOT EXISTS idx_order_items_product
                ON order_items(product_id);
        """)

    print("Database tables created successfully.")
