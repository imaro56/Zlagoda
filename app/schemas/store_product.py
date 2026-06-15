from decimal import Decimal
from pydantic import BaseModel, Field


class StoreProductCreate(BaseModel):
    upc: str = Field(min_length=1, max_length=12)
    upc_prom: str | None = None
    id_product: int
    selling_price: Decimal = Field(ge=0)
    products_number: int = Field(ge=0)
    promotional_product: bool = False


class StoreProductUpdate(BaseModel):      
    upc_prom: str | None = None
    id_product: int
    selling_price: Decimal = Field(ge=0)
    products_number: int = Field(ge=0)
    promotional_product: bool = False