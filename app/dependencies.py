from datetime import date
from psycopg.rows import dict_row
from app.db import pool
from app.queries.employee import get_employee
from fastapi import Depends, HTTPException
from starlette.requests import Request
from typing import Annotated, Optional
from pydantic import BeforeValidator


def _blank_to_none(v):
    return None if v in ("", None) else v

OptDate = Annotated[Optional[date], BeforeValidator(_blank_to_none)]
OptInt = Annotated[Optional[int], BeforeValidator(_blank_to_none)]


def get_conn():
    with pool.connection() as conn:
        yield conn

def get_db():
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur

class RequiresAuth(Exception):
    pass

def get_current_user(request: Request, cur=Depends(get_db)):
    id_employee = request.session.get("employee_id")
    if id_employee is None:
        raise RequiresAuth()
    employee = get_employee(cur, id_employee)
    if employee is None:
        request.session.clear()
        raise RequiresAuth()
    return employee

def requires_role(role):
    def checker(employee: dict=Depends(get_current_user)):
        if employee["empl_role"] != role:
            raise HTTPException(status_code=403)
        return employee
    return checker

CurrentUser = Annotated[dict, Depends(get_current_user)]
ManagerOnly = Annotated[dict, Depends(requires_role("manager"))]
CashierOnly = Annotated[dict, Depends(requires_role("cashier"))]
