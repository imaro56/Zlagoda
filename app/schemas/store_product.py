from decimal import Decimal
from pydantic import BaseModel, Field


class StoreProductCreate(BaseModel):
    upc: str = Field(min_length=1, max_length=12)
    id_product: int
    selling_price: Decimal = Field(ge=0)
    products_number: int = Field(ge=0)


class StoreProductUpdate(BaseModel):
    id_product: int
    products_number: int = Field(ge=0)