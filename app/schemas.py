from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)

    sku: str = Field(
        pattern=r"^[A-Z]{4}\d{3}$",
        description="Артикул товару, наприклад ELEC001",
    )

    category_id: int = Field(gt=0)

    price: Decimal = Field(
        ge=Decimal("0"),
        max_digits=10,
        decimal_places=2,
    )

    stock: int = Field(ge=0)


class ProductCreate(ProductBase):
    """Schema for creating a product."""


class ProductUpdate(ProductBase):
    """Schema for updating a product."""


class ProductRead(ProductBase):
    """Schema for returning a product."""

    id: int

    model_config = ConfigDict(from_attributes=True)
