from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import category
from app.templating import templates

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def categories_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categories": categories, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
def new_category_page(request: Request, user: ManagerOnly):
    return templates.TemplateResponse(
        request=request,
        name="new_category.html",
        context={"user": user}
    )


@router.post("/new", response_class=RedirectResponse)
def create_category(request: Request, user: ManagerOnly, category_name: str = Form(min_length=1, max_length=50), cur=Depends(get_db)):
    category.create_category(cur, {"category_name": category_name})
    return RedirectResponse(url="/categories", status_code=303)


@router.get("/{category_number}/edit", response_class=HTMLResponse)
def edit_category_page(request: Request, user: ManagerOnly, category_number: int, cur=Depends(get_db)):
    category_data = category.get_category(cur, category_number)
    if category_data is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(
        request=request,
        name="edit_category.html",
        context={"category": category_data, "user": user}
    )


@router.post("/{category_number}/edit", response_class=RedirectResponse)
def edit_category(request: Request, user: ManagerOnly, category_number: int, category_name: str = Form(min_length=1, max_length=50), cur=Depends(get_db)):
    category.update_category(cur, category_number, {"category_name": category_name})
    return RedirectResponse(url="/categories", status_code=303)


@router.post("/{category_number}/delete", response_class=RedirectResponse)
def delete_category(request: Request, user: ManagerOnly, category_number: int, cur=Depends(get_db)):
    category.delete_category(cur, category_number)
    return RedirectResponse(url="/categories", status_code=303)
