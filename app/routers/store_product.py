from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import store_product, product
from app.templating import templates

router = APIRouter(prefix="/store_products", tags=["store_products"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def store_products_page(request: Request, user: CurrentUser, sort: str = "quantity", cur=Depends(get_db)):
    if sort not in ("quantity", "name"):
        sort = "quantity"
    store_products = store_product.get_all_store_products(cur, sort)
    return templates.TemplateResponse(
        request=request,
        name="store_products.html",
        context={"store_products": store_products, "user": user, "sort": sort},
    )


@router.get("/new", response_class=HTMLResponse)
def new_store_product_page(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    products = product.get_all_products(cur)
    return templates.TemplateResponse(
        request=request,
        name="new_store_product.html",
        context={"user": user, "products": products},
    )


@router.post("/", response_class=Response)
def create_store_product(user: ManagerOnly,
        upc: str = Form(min_length=1, max_length=12),
        upc_prom: str = Form(default=""),
        id_product: int = Form(...),
        selling_price: Decimal = Form(ge=0),
        products_number: int = Form(ge=0),
        promotional_product: bool = Form(False),
        cur=Depends(get_db)):
    store_product.create_store_product(cur, upc, {
        "UPC_prom": upc_prom or None,
        "id_product": id_product,
        "selling_price": selling_price,
        "products_number": products_number,
        "promotional_product": promotional_product,
    })
    return Response(status_code=200, headers={"HX-Redirect": "/store_products"})


@router.get("/{upc}/edit", response_class=HTMLResponse)
def edit_store_product_page(request: Request, user: ManagerOnly, upc: str, cur=Depends(get_db)):
    store_product_data = store_product.get_store_product(cur, upc)
    if store_product_data is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    products = product.get_all_products(cur)
    return templates.TemplateResponse(
        request=request,
        name="edit_store_product.html",
        context={"store_product": store_product_data, "products": products, "user": user},
    )


@router.put("/{upc}", response_class=Response)
def edit_store_product(user: ManagerOnly, upc: str,
        upc_prom: str = Form(default=""),
        id_product: int = Form(...),
        selling_price: Decimal = Form(ge=0),
        products_number: int = Form(ge=0),
        promotional_product: bool = Form(False),
        cur=Depends(get_db)):
    updated = store_product.update_store_product(cur, upc, {
        "UPC_prom": upc_prom or None,
        "id_product": id_product,
        "selling_price": selling_price,
        "products_number": products_number,
        "promotional_product": promotional_product,
    })
    if updated is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    return Response(status_code=200, headers={"HX-Redirect": "/store_products"})


@router.delete("/{upc}", response_class=Response)
def delete_store_product(request: Request, user: ManagerOnly, upc: str, cur=Depends(get_db)):
    try:
        deleted = store_product.delete_store_product(cur, upc)
    except ForeignKeyViolation:
        cur.connection.rollback()
        return templates.TemplateResponse(
            request=request,
            name="_store_product_row.html",
            context={"store_product": store_product.get_store_product(cur, upc),
                     "user": user, "error": "Cannot delete: this UPC is used in receipts or linked as a promo"},
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    return Response(status_code=200)