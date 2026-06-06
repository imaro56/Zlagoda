from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.db import pool
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.dependencies import RequiresAuth
from starlette.responses import RedirectResponse
from app.routers import auth, category, employee


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
#app.include_router(employee.router)

@app.exception_handler(RequiresAuth)
def requires_auth_handler(request: Request, exc: RequiresAuth):
    return RedirectResponse(url="/login", status_code=303)
