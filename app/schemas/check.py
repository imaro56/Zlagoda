
from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    UPC: str = Field(max_length=12)
    product_number: int = Field(gt=0)


class CheckCreate(BaseModel):
    sales: list[SaleCreate] = Field(min_length=1)
    card_number: str | None = Field(default=None, max_length=13)
    
