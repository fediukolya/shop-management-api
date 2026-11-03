import psycopg
from fastapi import Depends, FastAPI, HTTPException, status

from app.repositories import (
    PostgresProductRepository,
    ProductRepository,
)
from app.schemas import ProductCreate, ProductRead, ProductUpdate

app = FastAPI(
    title="Shop Management API",
    description="REST API для керування товарами магазину",
    version="1.0.0",
)


def get_product_repository() -> ProductRepository:
    """Повертає реалізацію сховища товарів."""
    return PostgresProductRepository()


@app.get("/")
def root():
    return {"message": "Shop Management API працює!"}


@app.get("/products", response_model=list[ProductRead])
def get_products(
    repository: ProductRepository = Depends(get_product_repository),
):
    """Отримує список усіх товарів."""
    return repository.list_products()


@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    repository: ProductRepository = Depends(get_product_repository),
):
    """Отримує один товар за його ID."""
    product = repository.get_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не знайдено",
        )

    return product


@app.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product: ProductCreate,
    repository: ProductRepository = Depends(get_product_repository),
):
    """Створює новий товар."""
    if not repository.category_exists(product.category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категорію не знайдено",
        )

    try:
        return repository.create_product(product.model_dump())

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар із таким артикулом вже існує",
        ) from None


@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product: ProductUpdate,
    repository: ProductRepository = Depends(get_product_repository),
):
    """Повністю оновлює інформацію про товар."""
    if not repository.category_exists(product.category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категорію не знайдено",
        )

    try:
        updated_product = repository.update_product(
            product_id,
            product.model_dump(),
        )

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар із таким артикулом вже існує",
        ) from None

    if updated_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не знайдено",
        )

    return updated_product


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    repository: ProductRepository = Depends(get_product_repository),
):
    """Видаляє товар за ID."""
    try:
        deleted_id = repository.delete_product(product_id)

    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Не можна видалити товар, який є у замовленнях",
        ) from None

    if deleted_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не знайдено",
        )

    return {
        "message": "Товар успішно видалено",
        "id": deleted_id,
    }
