from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation, RaiseException

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.templating import templates
from typing import Annotated
from datetime import datetime

from app.security import hash_password

router = APIRouter(prefix="/employees", tags=["employees"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def employees_page(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    employees = employee.get_all_employees(cur)
    return templates.TemplateResponse(
        request=request,
        name="employee_list.html",
        context={"employees": employees, "user": user},
    )


@router.get("/new", response_class=HTMLResponse)
def new_employee_page(request: Request, user: ManagerOnly):
    return templates.TemplateResponse(
        request=request,
        name="employee_new.html",
        context={"user": user},
    )

@router.post("/", response_class=HTMLResponse)
def create_employee(user: ManagerOnly, form: Annotated[EmployeeCreate, Form()], cur=Depends(get_db)):
    data = form.model_dump()
    data["password_hash"] = hash_password(data.pop("password"))
    try:
        employee.create_employee(cur, data)
    except RaiseException:
        cur.connection.rollback()
        return HTMLResponse('<p class="error">Employee must be 18 or older</p>', status_code=422)
    return Response(status_code=200, headers={"HX-Redirect": "/employees"})

@router.get("/me", response_class=HTMLResponse)
def employee_me_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, user["id_employee"])
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="employee_detail.html",
        context={"employee": employee_data, "user": user},
    )


@router.get("/print", response_class=HTMLResponse)
def employees_print(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    employees = employee.get_all_employees(cur)
    return templates.TemplateResponse(
        request=request,
        name="employee_print.html",
        context={"employees": employees, "user": user,
                 "generated_at": datetime.now(), "back_url": "/employees"},
    )


@router.get("/{id_employee}/edit", response_class=HTMLResponse)
def edit_employee_page(request: Request, user: ManagerOnly, id_employee: str, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, id_employee)
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="employee_edit.html",
        context={"employee": employee_data, "user": user},
    )


@router.put("/{id_employee}", response_class=HTMLResponse)
def edit_employee(user: ManagerOnly, id_employee: str, form: Annotated[EmployeeUpdate, Form()], cur=Depends(get_db)):
    data = form.model_dump()
    try:
        updated = employee.update_employee(cur, id_employee, data)
    except RaiseException:
        cur.connection.rollback()
        return HTMLResponse('<p class="error">Employee must be 18 or older</p>', status_code=422)
    if updated is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Response(status_code=200, headers={"HX-Redirect": f"/employees/{id_employee}"})


@router.get("/promo_only", response_class=HTMLResponse)
def get_cashiers_promo_only(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    rows = employee.cashiers_with_only_promo_checks(cur)
    return templates.TemplateResponse(
        request=request,
        name="promo_only_cashiers.html",
        context={"rows": rows, "user": user},
    )


@router.get("/{id_employee}", response_class=HTMLResponse)
def employee_page(request: Request, user: ManagerOnly, id_employee: str, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, id_employee)
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="employee_detail.html",
        context={"employee": employee_data, "user": user},
    )


@router.delete("/{id_employee}")
def delete_employee(user: ManagerOnly, id_employee: str, cur=Depends(get_db)):
    if id_employee == user["id_employee"]:
          return HTMLResponse('<span class="error">You cannot delete your own account</span>')
    try: 
        deleted = employee.delete_employee(cur, id_employee)
    except ForeignKeyViolation:
        cur.connection.rollback()
        return HTMLResponse('<span class="error">Cannot delete employee with checks</span>')
    if deleted is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Response(status_code=200, headers={"HX-Redirect": "/employees"})