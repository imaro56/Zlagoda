from fastapi import APIRouter, Depends, Form, Request
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