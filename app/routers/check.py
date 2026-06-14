from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentUser, ManagerOnly, CashierOnly, get_current_user, get_db
from app.queries import check, employee, product
from app.templating import templates

router = APIRouter(prefix="/checks", tags=["checks"], dependencies=[Depends(get_current_user)])


@router.get("/mine", response_class=HTMLResponse)
def my_checks_page(request: Request, user: CurrentUser,
        date_from: date | None = None, date_to: date | None = None, cur=Depends(get_db)):
    today = date.today()
    if date_from is None:
        date_from = today
    if date_to is None:
        date_to = today
    checks = check.get_checks_by_cashier(cur, user["id_employee"], date_from, date_to)
    total = check.sum_checks_by_cashier(cur, user["id_employee"], date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="my_checks.html",
        context={"checks": checks, "total": total,
                 "date_from": date_from, "date_to": date_to, "user": user},
    )

@router.get("/reports/all", response_class=HTMLResponse)
def report_all(request: Request, user: ManagerOnly,
        date_from: date | None = None, date_to: date | None = None, cur=Depends(get_db)):
    checks = total = None
    if date_from and date_to:
        checks = check.get_all_checks(cur, date_from, date_to)
        total = check.sum_checks_all(cur, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_all.html",
        context={"checks": checks, "total": total,
                 "date_from": date_from, "date_to": date_to, "user": user},
    )


@router.get("/reports/by-cashier", response_class=HTMLResponse)
def report_by_cashier(request: Request, user: ManagerOnly, id_employee: str | None = None,
        date_from: date | None = None, date_to: date | None = None, cur=Depends(get_db)):
    cashiers = employee.get_all_cashiers(cur)
    checks = total = None
    if id_employee and date_from and date_to:
        checks = check.get_checks_by_cashier(cur, id_employee, date_from, date_to)
        total = check.sum_checks_by_cashier(cur, id_employee, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_by_cashier.html",
        context={"cashiers": cashiers, "checks": checks, "total": total,
                 "id_employee": id_employee, "date_from": date_from, "date_to": date_to, "user": user},
    )


@router.get("/reports/product", response_class=HTMLResponse)
def report_product(request: Request, user: ManagerOnly, id_product: int | None = None,
        date_from: date | None = None, date_to: date | None = None, cur=Depends(get_db)):
    products = product.get_all_products(cur)
    qty = None
    if id_product and date_from and date_to:
        qty = check.product_qty_sold(cur, id_product, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_product.html",
        context={"products": products, "qty": qty, "id_product": id_product,
                 "date_from": date_from, "date_to": date_to, "user": user},
    )

@router.get("/{check_number}", response_class=HTMLResponse)
def check_detail_page(request: Request, user: CurrentUser, check_number: str, cur=Depends(get_db)):
    check_data = check.get_check_with_items(cur, check_number)
    if check_data is None:
        raise HTTPException(status_code=404, detail="Check not found")
    return templates.TemplateResponse(
        request=request,
        name="check_detail.html",
        context={"check": check_data, "user": user},
    )