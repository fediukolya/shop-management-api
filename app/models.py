from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Category:
    name: str
    description: str | None = None
    id: int | None = None


@dataclass
class Product:
    name: str
    sku: str
    category_id: int
    price: Decimal
    stock: int
    id: int | None = None


@dataclass
class Customer:
    full_name: str
    email: str
    phone: str | None = None
    id: int | None = None


@dataclass
class Order:
    customer_id: int
    status: str = "new"
    created_at: datetime | None = None
    id: int | None = None


@dataclass
class OrderItem:
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    id: int | None = None
