from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.db import pool
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.dependencies import RequiresAuth
from starlette.responses import RedirectResponse
from app.routers import auth, category, employee, customer_card, product, store_product, check
from fastapi.exceptions import RequestValidationError
from starlette.responses import HTMLResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()

app = FastAPI(name="Zlagoda", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(employee.router)

app.include_router(customer_card.router)
app.include_router(product.router)
app.include_router(store_product.router)
app.include_router(check.router)

@app.exception_handler(RequiresAuth)
def requires_auth_handler(request: Request, exc: RequiresAuth):
    return RedirectResponse(url="/login", status_code=303)

@app.exception_handler(RequestValidationError)
def validation_handler(request: Request, exc: RequestValidationError):
    msg = "; ".join(e["msg"] for e in exc.errors())
    return HTMLResponse(f'<p class="error">{msg}</p>', status_code=422)