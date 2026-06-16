from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import category
from app.templating import templates
from datetime import datetime

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def categories_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request,
        name="category_list.html",
        context={"categories": categories, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
def new_category_page(request: Request, user: ManagerOnly):
    return templates.TemplateResponse(
        request=request,
        name="category_new.html",
        context={"user": user}
    )


@router.post("/", response_class=Response)
def create_category(user: ManagerOnly, category_name: str = Form(min_length=1, max_length=50), cur=Depends(get_db)):
    category.create_category(cur, {"category_name": category_name})
    return Response(status_code=200, headers={"HX-Redirect": "/categories"})


@router.get("/{category_number}/edit", response_class=HTMLResponse)
def edit_category_page(request: Request, user: ManagerOnly, category_number: int, cur=Depends(get_db)):
    category_data = category.get_category(cur, category_number)
    if category_data is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(
        request=request,
        name="category_edit.html",
        context={"category": category_data, "user": user}
    )


@router.put("/{category_number}", response_class=Response)
def edit_category(user: ManagerOnly, category_number: int, category_name: str = Form(min_length=1, max_length=50), cur=Depends(get_db)):
    updated = category.update_category(cur, category_number, {"category_name": category_name})
    if updated is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Response(status_code=200, headers={"HX-Redirect": "/categories"})


@router.delete("/{category_number}", response_class=Response)
def delete_category(request: Request, user: ManagerOnly, category_number: int, cur=Depends(get_db)):
    try:
        deleted = category.delete_category(cur, category_number)
    except ForeignKeyViolation:
        cur.connection.rollback()
        return templates.TemplateResponse(
            request=request,
            name="_category_row.html",
            context={"category": category.get_category(cur, category_number),
                    "user": user, "error": "Cannot delete category with products"}
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Response(status_code=200)


@router.get("/print", response_class=HTMLResponse)
def categories_print(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request,
        name="category_print.html",
        context={"categories": categories, "user": user,
                 "generated_at": datetime.now(), "back_url": "/categories"},
    )
    