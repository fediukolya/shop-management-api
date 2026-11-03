from decimal import Decimal

from app.database import get_connection


def seed_database():
    """Додає тестові українські дані до бази магазину."""

    categories = [
        ("Електроніка", "Електронні пристрої та аксесуари"),
        ("Одяг", "Одяг та модні аксесуари"),
        ("Книги", "Навчальна та художня література"),
        ("Дім і побут", "Товари для дому та кухні"),
        ("Спорт", "Спортивне обладнання та аксесуари"),
    ]

    products = [
        ("ELEC001", "Бездротові навушники", "Електроніка", "2499.00", 25),
        ("ELEC002", "Комп'ютерна миша", "Електроніка", "799.00", 40),
        ("ELEC003", "Механічна клавіатура", "Електроніка", "1899.00", 15),
        ("ELEC004", "Флешнакопичувач 64 ГБ", "Електроніка", "299.00", 60),
        ("ELEC005", "Підставка для ноутбука", "Електроніка", "649.00", 20),
        ("CLOT001", "Бавовняна футболка", "Одяг", "450.00", 35),
        ("CLOT002", "Сині джинси", "Одяг", "1299.00", 18),
        ("CLOT003", "Худі", "Одяг", "999.00", 22),
        ("CLOT004", "Зимова куртка", "Одяг", "2899.00", 10),
        ("CLOT005", "Бейсболка", "Одяг", "350.00", 30),
        ("BOOK001", "Програмування на Python", "Книги", "650.00", 12),
        ("BOOK002", "Чистий код", "Книги", "850.00", 14),
        ("BOOK003", "Системи баз даних", "Книги", "720.00", 9),
        ("BOOK004", "Основи кібербезпеки", "Книги", "590.00", 17),
        ("BOOK005", "Алгоритми та структури даних", "Книги", "780.00", 11),
        ("HOME001", "Кавоварка", "Дім і побут", "2199.00", 8),
        ("HOME002", "Електричний чайник", "Дім і побут", "899.00", 16),
        ("HOME003", "Настільна лампа", "Дім і побут", "549.00", 24),
        ("HOME004", "Кухонні ваги", "Дім і побут", "399.00", 19),
        ("HOME005", "Пляшка для води", "Дім і побут", "250.00", 32),
        ("SPRT001", "Килимок для йоги", "Спорт", "499.00", 21),
        ("SPRT002", "Набір гантелей", "Спорт", "1599.00", 7),
        ("SPRT003", "Футбольний м'яч", "Спорт", "699.00", 13),
        ("SPRT004", "Скакалка", "Спорт", "199.00", 28),
        ("SPRT005", "Фітнес-браслет", "Спорт", "349.00", 26),
    ]

    customers = [
        ("Олександр Петренко", "alex@example.com", "+380501112233"),
        ("Марія Коваленко", "maria@example.com", "+380671234567"),
        ("Іван Шевченко", "ivan@example.com", "+380931234567"),
        ("Анна Мельник", "anna@example.com", "+380991234567"),
        ("Дмитро Бондаренко", "dmytro@example.com", "+380681234567"),
        ("Софія Ткаченко", "sofia@example.com", "+380731234567"),
        ("Андрій Кравченко", "andrii@example.com", "+380951234567"),
        ("Олена Мороз", "olena@example.com", "+380631234567"),
        ("Максим Лисенко", "max@example.com", "+380671111222"),
        ("Наталія Савченко", "natalia@example.com", "+380501234567"),
    ]

    # Статуси відповідають обмеженням CHECK у таблиці orders.
    statuses = [
        "new",
        "processing",
        "completed",
        "completed",
        "new",
        "processing",
        "completed",
        "new",
        "cancelled",
        "completed",
    ]

    with get_connection() as conn:
        existing = conn.execute("SELECT EXISTS (SELECT 1 FROM categories)").fetchone()[
            "exists"
        ]

        if existing:
            print("База вже містить дані. Повторне заповнення пропущено.")
            return

        # Додавання категорій
        category_ids = {}

        for name, description in categories:
            row = conn.execute(
                """
                INSERT INTO categories (name, description)
                VALUES (%s, %s)
                RETURNING id
                """,
                (name, description),
            ).fetchone()

            category_ids[name] = row["id"]

        # Додавання товарів
        product_ids = {}
        product_prices = {}

        for sku, name, category, price, stock in products:
            row = conn.execute(
                """
                INSERT INTO products
                    (name, sku, category_id, price, stock)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    name,
                    sku,
                    category_ids[category],
                    Decimal(price),
                    stock,
                ),
            ).fetchone()

            product_ids[sku] = row["id"]
            product_prices[sku] = Decimal(price)

        # Додавання покупців
        customer_ids = []

        for full_name, email, phone in customers:
            row = conn.execute(
                """
                INSERT INTO customers (full_name, email, phone)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (full_name, email, phone),
            ).fetchone()

            customer_ids.append(row["id"])

        # Додавання замовлень та позицій замовлень
        product_skus = list(product_ids.keys())

        for i, customer_id in enumerate(customer_ids):
            order = conn.execute(
                """
                INSERT INTO orders (customer_id, status)
                VALUES (%s, %s)
                RETURNING id
                """,
                (customer_id, statuses[i]),
            ).fetchone()

            order_id = order["id"]

            for sku in product_skus[i * 2 : i * 2 + 2]:
                conn.execute(
                    """
                    INSERT INTO order_items
                        (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        product_ids[sku],
                        i % 3 + 1,
                        product_prices[sku],
                    ),
                )

    print("Тестові дані успішно додано!")
    print("Категорії: 5")
    print("Товари: 25")
    print("Покупці: 10")
    print("Замовлення: 10")
    print("Позиції замовлень: 20")
    print("ЗАГАЛОМ: 70 записів")


if __name__ == "__main__":
    seed_database()
