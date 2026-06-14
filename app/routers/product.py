from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import product, category
from app.templating import templates

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def products_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    products = product.get_all_products(cur)
    return templates.TemplateResponse(
        request=request,
        name="product_list.html",
        context={"products": products, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
def new_product_page(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request, name="product_new.html",
        context={"user": user, "categories": categories},
    )


@router.post("/", response_class=Response)
def create_product(user: ManagerOnly,
        product_name: str = Form(min_length=1, max_length=50),
        category_number: int = Form(...),
        characteristics: str = Form(min_length=1, max_length=100),
        cur=Depends(get_db)):
    product.create_product(cur, {
        "product_name": product_name,
        "category_number": category_number,
        "characteristics": characteristics,
    })
    return Response(status_code=200, headers={"HX-Redirect": "/products"})


@router.get("/{id_product}/edit", response_class=HTMLResponse)
def edit_product_page(request: Request, user: ManagerOnly, id_product: int, cur=Depends(get_db)):
    product_data = product.get_product(cur, id_product)
    if product_data is None:
        raise HTTPException(status_code=404, detail="Product not found")
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request,
        name="product_edit.html",
        context={"product": product_data, "categories": categories, "user": user},
    )


@router.put("/{id_product}", response_class=Response)
def edit_product(user: ManagerOnly, id_product: int,
        product_name: str = Form(min_length=1, max_length=50),
        category_number: int = Form(...),
        characteristics: str = Form(min_length=1, max_length=100),
        cur=Depends(get_db)):
    updated = product.update_product(cur, id_product, {
        "product_name": product_name,
        "category_number": category_number,
        "characteristics": characteristics,
    })
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=200, headers={"HX-Redirect": "/products"})


@router.delete("/{id_product}", response_class=Response)
def delete_product(request: Request, user: ManagerOnly, id_product: int, cur=Depends(get_db)):
    try:
        deleted = product.delete_product(cur, id_product)
    except ForeignKeyViolation:
        cur.connection.rollback()
        return templates.TemplateResponse(
            request=request,
            name="_product_row.html",
            context={"product": product.get_product(cur, id_product),
                    "user": user, "error": "Cannot delete product that is in stock"},
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=200)