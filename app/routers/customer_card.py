from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from psycopg.errors import ForeignKeyViolation

from app.dependencies import CurrentUser, ManagerOnly, get_current_user, get_db
from app.queries import customer_card
from app.templating import templates

from typing import Annotated
from datetime import datetime
from app.schemas.customer_card import CustomerCardCreate, CustomerCardUpdate

router = APIRouter(prefix="/customer_cards", tags=["customer_cards"], dependencies=[Depends(get_current_user)])


@router.get("/", response_class=HTMLResponse)
def customer_cards_page(request: Request, user: CurrentUser, cur=Depends(get_db)):
    customer_cards = customer_card.get_all_cards(cur)
    return templates.TemplateResponse(
        request=request,
        name="customer_card_list.html",
        context={"customer_cards": customer_cards, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
def new_customer_card_page(request: Request, user: CurrentUser):
    return templates.TemplateResponse(
        request=request,
        name="customer_card_new.html",
        context={"user": user}
    )


@router.post("/", response_class=Response)
def create_customer_card(user: CurrentUser, form: Annotated[CustomerCardCreate, Form()], cur=Depends(get_db)):
    customer_card.create_card(cur, form.model_dump())
    return Response(status_code=200, headers={"HX-Redirect": "/customer_cards"})


@router.get("/{card_number}/edit", response_class=HTMLResponse)
def edit_customer_card_page(request: Request, user: CurrentUser, card_number: str, cur=Depends(get_db)):
    customer_card_data = customer_card.get_card(cur, card_number)
    if customer_card_data is None:
        raise HTTPException(status_code=404, detail="Customer card not found")
    return templates.TemplateResponse(
        request=request,
        name="customer_card_edit.html",
        context={"customer_card": customer_card_data, "user": user}
    )


@router.put("/{card_number}", response_class=Response)
def edit_customer_card(user: CurrentUser, card_number: str, form: Annotated[CustomerCardUpdate, Form()], cur=Depends(get_db)):
    updated = customer_card.update_card(cur, card_number, form.model_dump())
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
    

@router.get("/print", response_class=HTMLResponse)
def customer_cards_print(request: Request, user: ManagerOnly, cur=Depends(get_db)):
    customer_cards = customer_card.get_all_cards(cur)
    return templates.TemplateResponse(
        request=request,
        name="customer_print.html",
        context={"customer_cards": customer_cards, "user": user,
                 "generated_at": datetime.now(), "back_url": "/customer_cards"},
    )
