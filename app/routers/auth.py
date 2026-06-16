from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import get_db
from app.security import verify_password
from app.templating import templates
from app.queries import employee as employee_queries

router = APIRouter(tags=["login"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )

@router.post("/login")
def login(request: Request, login: str = Form(...), password: str = Form(...), cur=Depends(get_db)):
    employee = employee_queries.get_employee_by_login(cur, login)
    if employee is None or not verify_password(password, employee["password_hash"]):
        return templates.TemplateResponse(
              request=request,
              name="login.html",
              context={"error": "Wrong login or password"},
              status_code=401,
          )
    request.session["employee_id"] = employee["id_employee"]
    next = "/checks/sale" if employee["empl_role"] == "cashier" else "/employees/"
    return RedirectResponse(url=next, status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
