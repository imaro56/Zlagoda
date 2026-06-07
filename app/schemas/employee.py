from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class EmployeeCreate(BaseModel):
    id_employee: str = Field(max_length=10)
    empl_surname: str = Field(min_length=1, max_length=50)
    empl_name: str = Field(min_length=1, max_length=50)
    empl_patronymic: str | None = None
    empl_role: Literal["manager", "cashier"]
    salary: Decimal = Field(ge=0)
    date_of_birth: date
    date_of_start: date
    phone_number: str = Field(max_length=13)
    city: str = Field(max_length=50)
    street: str = Field(max_length=50)
    zip_code: str = Field(max_length=9)
    login: str
    password: str = Field(min_length=8)


class EmployeeUpdate(BaseModel):
    empl_surname: str = Field(min_length=1, max_length=50)
    empl_name: str = Field(min_length=1, max_length=50)
    empl_patronymic: str | None = None
    empl_role: Literal["manager", "cashier"]
    salary: Decimal = Field(ge=0)
    date_of_birth: date
    date_of_start: date
    phone_number: str = Field(max_length=13)
    city: str = Field(max_length=50)
    street: str = Field(max_length=50)
    zip_code: str = Field(max_length=9)