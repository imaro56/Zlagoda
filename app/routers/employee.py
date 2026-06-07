from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.templating import templates
from typing import Annotated

from app.security import hash_password

router = APIRouter(prefix="/employees", tags=["employees"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def employees_page(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    employees = employee.get_all_employees(cur)
    return templates.TemplateResponse(
        request=request,
        name="employees.html",
        context={"employees": employees, "user": user},
    )


@router.get("/new", response_class=HTMLResponse)
def new_employee_page(request: Request, user: ManagerOnly):
    return templates.TemplateResponse(
        request=request,
        name="new_employee.html",
        context={"user": user},
    )


@router.post("/", response_class=HTMLResponse)
def create_employee(user: ManagerOnly, form: Annotated[EmployeeCreate, Form()], cur=Depends(get_db)):
    data = form.model_dump()
    data["password_hash"] = hash_password(data.pop("password"))
    employee.create_employee(cur, data)
    return Response(status_code=200, headers={"HX-Redirect": "/employees"})

@router.get("/me", response_class=HTMLResponse)
def employee_me_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, user["id_employee"])
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="employee.html",
        context={"employee": employee_data, "user": user},
    )

@router.get("/{employee_id}/edit", response_class=HTMLResponse)
def edit_employee_page(request: Request, user: ManagerOnly, employee_id: str, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, employee_id)
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="edit_employee.html",
        context={"employee": employee_data, "user": user},
    )

@router.put("/{employee_id}", response_class=HTMLResponse)
def edit_employee(user: ManagerOnly, employee_id: str, form: Annotated[EmployeeUpdate, Form()], cur=Depends(get_db)):
    data = form.model_dump()
    updated = employee.update_employee(cur, employee_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Response(status_code=200, headers={"HX-Redirect": f"/employees/{employee_id}"})


@router.get("/{employee_id}", response_class=HTMLResponse)
def employee_page(request: Request, user: ManagerOnly, employee_id: str, cur=Depends(get_db)):
    employee_data = employee.get_employee(cur, employee_id)
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request=request,
        name="employee.html",
        context={"employee": employee_data, "user": user},
    )

