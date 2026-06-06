from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.dependencies import get_current_user, get_db, CurrentUser
from app.templating import templates
from app.queries import category

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def categories_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    categories = category.get_all_categories(cur)
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categories": categories, "user": user}
    )
