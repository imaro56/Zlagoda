from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import store_product, product
from app.templating import templates
from datetime import datetime
from decimal import Decimal

from typing import Annotated
from app.schemas.store_product import StoreProductCreate, StoreProductUpdate

router = APIRouter(prefix="/store_products", tags=["store_products"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def store_products_page(request: Request, user: CurrentUser, sort: str = "quantity", promo: str = "all", upc: str = "", cur=Depends(get_db)):
    if sort not in ("quantity", "name"):
        sort = "quantity"
    if upc.strip():
        found = store_product.get_store_product_full(cur, upc.strip())
        store_products = [found] if found else []
    elif promo == "yes":
        store_products = store_product.get_promotional_store_products(cur, sort)
    elif promo == "no":
        store_products = store_product.get_non_promotional_store_products(cur, sort)
    else:
        store_products = store_product.get_all_store_products(cur, sort)
    return templates.TemplateResponse(
        request=request,
        name="store_products.html",
        context={"store_products": store_products, "user": user, "sort": sort,
                 "promo": promo, "upc": upc},
    )


@router.get("/new", response_class=HTMLResponse)
def store_product_new_page(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    products = product.get_all_products(cur)
    return templates.TemplateResponse(
        request=request,
        name="store_product_new.html",
        context={"user": user, "products": products},
    )


@router.post("/", response_class=Response)
def create_store_product(user: ManagerOnly, form: Annotated[StoreProductCreate, Form()], cur=Depends(get_db)):
    try: 
        store_product.create_store_product(cur, form.upc, {
            "UPC_prom": None,
            "id_product": form.id_product,
            "selling_price": form.selling_price,
            "products_number": form.products_number,
            "promotional_product": False,
        })
    except UniqueViolation:
        cur.connection.rollback()
        return HTMLResponse('<p class="error">This product already has a regular store entry</p>', status_code=422)
    return Response(status_code=200, headers={"HX-Redirect": "/store_products"})


@router.get("/{upc}/edit", response_class=HTMLResponse)
def store_product_edit_page(request: Request, user: ManagerOnly, upc: str, cur=Depends(get_db)):
    store_product_data = store_product.get_store_product(cur, upc)
    if store_product_data is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    products = product.get_all_products(cur)
    return templates.TemplateResponse(
        request=request,
        name="store_product_edit.html",
        context={"store_product": store_product_data, "products": products, "user": user},
    )


@router.put("/{upc}", response_class=Response)
def edit_store_product(user: ManagerOnly, upc: str, form: Annotated[StoreProductUpdate, Form()], cur=Depends(get_db)):
    existing = store_product.get_store_product(cur, upc)
    if existing is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    store_product.update_store_product(cur, upc, {
        "UPC_prom": existing["upc_prom"],
        "id_product": form.id_product,
        "selling_price": existing["selling_price"],
        "products_number": form.products_number,
        "promotional_product": existing["promotional_product"],
    })
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


@router.get("/print", response_class=HTMLResponse)
def store_products_print(request: Request, user: ManagerOnly, sort: str = "quantity", cur=Depends(get_db)):
    if sort not in ("quantity", "name"):
        sort = "quantity"
    store_products = store_product.get_all_store_products(cur, sort)
    return templates.TemplateResponse(
        request=request,
        name="store_product_print.html",
        context={"store_products": store_products, "user": user,
                 "generated_at": datetime.now(), "back_url": "/store_products"},
    )


@router.get("/{upc}/reprice", response_class=HTMLResponse)
def store_product_reprice_page(request: Request, user: ManagerOnly, upc: str, cur=Depends(get_db)):
    sp = store_product.get_store_product_full(cur, upc)
    if sp is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    return templates.TemplateResponse(
        request=request, name="store_product_reprice.html",
        context={"store_product": sp, "user": user},
    )


@router.post("/{upc}/reprice", response_class=Response)
def reprice_store_product(user: ManagerOnly, upc: str, new_price: Decimal = Form(ge=0), cur=Depends(get_db)):
    sp = store_product.get_store_product(cur, upc)
    if sp is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    store_product.reprice_store_product(cur, sp["id_product"], new_price)
    return Response(status_code=200, headers={"HX-Redirect": "/store_products"})


@router.get("/{upc}/promote", response_class=HTMLResponse)
def store_product_promote_page(request: Request, user: ManagerOnly, upc: str, cur=Depends(get_db)):
    sp = store_product.get_store_product_full(cur, upc)
    if sp is None:
        raise HTTPException(status_code=404, detail="Store product not found")
    return templates.TemplateResponse(
        request=request, name="store_product_promote.html",
        context={"store_product": sp, "user": user},
    )


@router.post("/{upc}/promote", response_class=Response)
def promote_store_product(user: ManagerOnly, upc: str, upc_prom: str = Form(min_length=1, max_length=12), products_number: int = Form(ge=0), cur=Depends(get_db)):
    promo = store_product.create_promotional_store_product(cur, upc, upc_prom, products_number)
    if promo is None:
        return HTMLResponse('<p class="error">This product is promotional or has a promo row</p>', status_code=422)
    return Response(status_code=200, headers={"HX-Redirect": "/store_products"})
