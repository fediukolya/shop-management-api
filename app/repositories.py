from typing import Any, Protocol

from app.database import get_connection


class ProductRepository(Protocol):
    """Інтерфейс для роботи з товарами."""

    def list_products(self) -> list[dict[str, Any]]: ...

    def get_product(self, product_id: int) -> dict[str, Any] | None: ...

    def category_exists(self, category_id: int) -> bool: ...

    def create_product(self, product: dict[str, Any]) -> dict[str, Any]: ...

    def update_product(
        self,
        product_id: int,
        product: dict[str, Any],
    ) -> dict[str, Any] | None: ...

    def delete_product(self, product_id: int) -> int | None: ...


class PostgresProductRepository:
    """Реалізація сховища товарів для PostgreSQL."""

    def list_products(self) -> list[dict[str, Any]]:
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT id, name, sku, category_id, price, stock
                FROM products
                ORDER BY id
                """
            ).fetchall()

    def get_product(self, product_id: int) -> dict[str, Any] | None:
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT id, name, sku, category_id, price, stock
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            ).fetchone()

    def category_exists(self, category_id: int) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM categories WHERE id = %s",
                (category_id,),
            ).fetchone()

        return row is not None

    def create_product(self, product: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            return conn.execute(
                """
                INSERT INTO products
                    (name, sku, category_id, price, stock)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, sku, category_id, price, stock
                """,
                (
                    product["name"],
                    product["sku"],
                    product["category_id"],
                    product["price"],
                    product["stock"],
                ),
            ).fetchone()

    def update_product(
        self,
        product_id: int,
        product: dict[str, Any],
    ) -> dict[str, Any] | None:
        with get_connection() as conn:
            return conn.execute(
                """
                UPDATE products
                SET name = %s,
                    sku = %s,
                    category_id = %s,
                    price = %s,
                    stock = %s
                WHERE id = %s
                RETURNING id, name, sku, category_id, price, stock
                """,
                (
                    product["name"],
                    product["sku"],
                    product["category_id"],
                    product["price"],
                    product["stock"],
                    product_id,
                ),
            ).fetchone()

    def delete_product(self, product_id: int) -> int | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                DELETE FROM products
                WHERE id = %s
                RETURNING id
                """,
                (product_id,),
            ).fetchone()

        return row["id"] if row else None
