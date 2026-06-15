from pydantic import BaseModel, Field


class ProductForm(BaseModel):
    product_name: str = Field(min_length=1, max_length=50)
    category_number: int
    characteristics: str = Field(min_length=1, max_length=100)