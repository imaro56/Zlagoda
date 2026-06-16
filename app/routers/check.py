from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentUser, ManagerOnly, CashierOnly, get_current_user, get_db, get_conn, OptDate, OptInt
from app.queries import check, employee, product, store_product, customer_card
from app.templating import templates
from app.schemas.check import CheckCreate, SaleCreate
from pydantic import ValidationError

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
def report_all(request: Request, user: ManagerOnly, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    checks = check.get_all_checks(cur, date_from, date_to)
    total = check.sum_checks_all(cur, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_all.html",
        context={"checks": checks, "total": total,
                 "date_from": date_from, "date_to": date_to, "user": user},
    )


@router.get("/reports/by-cashier", response_class=HTMLResponse)
def report_by_cashier(request: Request, user: ManagerOnly, id_employee: str | None = None, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    cashiers = employee.get_all_cashiers(cur)
    checks = total = None
    if id_employee:
        checks = check.get_checks_by_cashier(cur, id_employee, date_from, date_to)
        total = check.sum_checks_by_cashier(cur, id_employee, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_by_cashier.html",
        context={"cashiers": cashiers, "checks": checks, "total": total,
                 "id_employee": id_employee, "date_from": date_from, "date_to": date_to, "user": user},
    )


@router.get("/reports/product", response_class=HTMLResponse)
def report_product(request: Request, user: ManagerOnly, id_product: OptInt = None, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    products = product.get_all_products(cur)
    qty = None
    if id_product is not None:
        qty = check.product_qty_sold(cur, id_product, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_product.html",
        context={"products": products, "qty": qty, "id_product": id_product,
                 "date_from": date_from, "date_to": date_to, "user": user},
    )


@router.get("/sale", response_class=HTMLResponse)
def sale_page(request: Request, user: CashierOnly, cur=Depends(get_db)):
    store_products = store_product.get_all_store_products(cur, "name")
    cards = customer_card.get_all_cards(cur)
    return templates.TemplateResponse(
        request=request,
        name="sale.html",
        context={"store_products": store_products, "cards": cards, "user": user},
    )

@router.get("/reports/sales_by_cashier", response_class=HTMLResponse)
def report_sales_by_cashier(request: Request, user: ManagerOnly,
        date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    rows = None
    if date_from and date_to:
        rows = check.sales_by_cashier(cur, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_sales_by_cashier.html",
        context={"rows": rows, "date_from": date_from, "date_to": date_to, "user": user},
    )

@router.get("/reports/categories_all_sold", response_class=HTMLResponse)
def report_categories_all_sold(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    rows = check.categories_all_products_sold(cur)
    return templates.TemplateResponse(
        request=request,
        name="report_categories_all_sold.html",
        context={"rows": rows, "user": user},
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


@router.post("/", response_class=Response)
def create_check(user: CashierOnly, upc: list[str] = Form([]), product_number: list[int] = Form([]), card_number: str = Form(""), conn=Depends(get_conn)):
    try:
        data = CheckCreate(sales=[SaleCreate(UPC=u, product_number=n) for u, n in zip(upc, product_number) if n > 0], card_number=card_number or None)
        check_number = check.create_check(conn, user["id_employee"], data)
        return Response(status_code=200, headers={"HX-Redirect": f"/checks/{check_number}"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Not valid")


@router.delete("/{check_number}", response_class=Response)
def delete_check(user: ManagerOnly, check_number: str, cur=Depends(get_db)):
    deleted = check.delete_check(cur, check_number)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Check not found")
    return Response(status_code=200)


@router.get("/reports/print", response_class=HTMLResponse)
def report_print(request: Request, user: ManagerOnly, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    checks = check.get_all_checks(cur, date_from, date_to)
    total = check.sum_checks_all(cur, date_from, date_to)
    return templates.TemplateResponse(
        request=request,
        name="report_print.html",
        context={"checks": checks, "total": total,
                 "date_from": date_from, "date_to": date_to,
                 "user": user, "generated_at": datetime.now(), "back_url": "/checks/reports/all"},
    )


@router.get("/reports/by-cashier/print", response_class=HTMLResponse)
def report_by_cashier_print(request: Request, user: ManagerOnly, id_employee: str, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    checks = check.get_checks_by_cashier(cur, id_employee, date_from, date_to)
    total = check.sum_checks_by_cashier(cur, id_employee, date_from, date_to)
    cashier = employee.get_employee(cur, id_employee)
    subtitle = f"Cashier: {cashier['empl_surname']} {cashier['empl_name']}" if cashier else None
    return templates.TemplateResponse(
        request=request,
        name="report_print.html",
        context={"checks": checks, "total": total, "subtitle": subtitle,
                 "date_from": date_from, "date_to": date_to,
                 "user": user, "generated_at": datetime.now(), "back_url": "/checks/reports/by-cashier"},
    )


@router.get("/reports/product/print", response_class=HTMLResponse)
def report_product_print(request: Request, user: ManagerOnly, id_product: int, date_from: OptDate = None, date_to: OptDate = None, cur=Depends(get_db)):
    qty = check.product_qty_sold(cur, id_product, date_from, date_to)
    product_data = product.get_product(cur, id_product)
    return templates.TemplateResponse(
        request=request,
        name="report_product_print.html",
        context={"qty": qty, "product": product_data,
                 "date_from": date_from, "date_to": date_to,
                 "user": user, "generated_at": datetime.now(), "back_url": "/checks/reports/product"},
    )