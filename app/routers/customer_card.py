from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import customer_card
from app.templating import templates

router = APIRouter(prefix="/customer_cards", tags=["customer_cards"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def customer_cards_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    customer_cards = customer_card.get_all_cards(cur)
    return templates.TemplateResponse(
        request=request,
        name="customer_cards.html",
        context={"customer_cards": customer_cards, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
def new_customer_card_page(request: Request, user: CurrentUser):
    return templates.TemplateResponse(
        request=request,
        name="new_customer_card.html",
        context={"user": user}
    )


@router.post("/", response_class=Response)
def create_customer_card(user: CurrentUser, card_number: str = Form(min_length=1, max_length=13),
            cust_surname:str = Form(min_length=1, max_length=50),
            cust_name: str = Form(min_length=1, max_length=50),
            cust_patronymic: str = Form(default="", max_length=50),
            phone_number: str = Form(min_length=1, max_length=13),
            city: str = Form(default="", max_length=50),
            street: str = Form(default="", max_length=50),
            zip_code: str = Form(default="", max_length=9),
            percent: int = Form(ge=0),
            cur = Depends(get_db),):
    customer_card.create_card(cur, {"card_number": card_number, "cust_surname": cust_surname, "cust_name": cust_name, "cust_patronymic": cust_patronymic, "phone_number": phone_number, "city": city, "street": street, "zip_code": zip_code, "percent": percent,})
    return Response(status_code=200, headers={"HX-Redirect": "/customer_cards"})


@router.get("/{card_number}/edit", response_class=HTMLResponse)
def edit_customer_card_page(request: Request, user: CurrentUser, card_number: str, cur=Depends(get_db)):
    customer_card_data = customer_card.get_card(cur, card_number)
    if customer_card_data is None:
        raise HTTPException(status_code=404, detail="Customer card not found")
    return templates.TemplateResponse(
        request=request,
        name="edit_customer_card.html",
        context={"customer_card": customer_card_data, "user": user}
    )


@router.put("/{card_number}", response_class=Response)
def edit_customer_card(user: CurrentUser, card_number: str,
            cust_surname: str = Form(min_length=1, max_length=50),
            cust_name: str = Form(min_length=1, max_length=50),
            cust_patronymic: str = Form(default="", max_length=50),
            phone_number: str = Form(min_length=1, max_length=13),
            city: str = Form(default="", max_length=50),
            street: str = Form(default="", max_length=50),
            zip_code: str = Form(default="", max_length=9),
            percent: int = Form(ge=0),
            cur=Depends(get_db)):
    updated = customer_card.update_card(cur, card_number, {
        "cust_surname": cust_surname, "cust_name": cust_name, "cust_patronymic": cust_patronymic,
        "phone_number": phone_number, "city": city, "street": street,
        "zip_code": zip_code, "percent": percent,
    })
    if updated is None:
        raise HTTPException(status_code=404, detail="Customer card not found")
    return Response(status_code=200, headers={"HX-Redirect": "/customer_cards"})


@router.delete("/{card_number}", response_class=Response)
def delete_customer_card(request: Request, user: ManagerOnly, card_number: str, cur=Depends(get_db)):
    try:
        deleted = customer_card.delete_card(cur, card_number)
    except ForeignKeyViolation:
        cur.connection.rollback()
        return templates.TemplateResponse(
            request=request,
            name="_customer_card_row.html",
            context={"customer_card": customer_card.get_card(cur, card_number),
                    "user": user, "error": "Cannot delete a card used by receipts"}
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Customer card not found")
    return Response(status_code=200)