from pydantic import BaseModel, Field


class CustomerCardCreate(BaseModel):
    card_number: str = Field(min_length=1, max_length=13)
    cust_surname: str = Field(min_length=1, max_length=50)
    cust_name: str = Field(min_length=1, max_length=50)
    cust_patronymic: str | None = None
    phone_number: str = Field(min_length=1, max_length=13)
    city: str | None = Field(default=None, max_length=50)
    street: str | None = Field(default=None, max_length=50)
    zip_code: str | None = Field(default=None, max_length=9)
    percent: int = Field(ge=0)


class CustomerCardUpdate(BaseModel):
    cust_surname: str = Field(min_length=1, max_length=50)
    cust_name: str = Field(min_length=1, max_length=50)
    cust_patronymic: str | None = None
    phone_number: str = Field(min_length=1, max_length=13)
    city: str | None = Field(default=None, max_length=50)
    street: str | None = Field(default=None, max_length=50)
    zip_code: str | None = Field(default=None, max_length=9)
    percent: int = Field(ge=0)