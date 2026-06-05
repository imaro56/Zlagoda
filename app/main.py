from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import pool
from fastapi.staticfiles import StaticFiles
from app.routers import category
from starlette.middleware.sessions import SessionMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()

app = FastAPI(name="Zlagoda", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(category.router)
