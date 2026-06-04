from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.dependencies import get_db
from app.templating import templates

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_class=HTMLResponse)
def categories_page(request: Request, cur=Depends(get_db)):
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categories": categories}
    )
