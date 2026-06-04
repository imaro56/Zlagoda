from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import pool
from fastapi.staticfiles import StaticFiles
from app.routers import category


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()

app = FastAPI(name="Zlagoda", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(category.router)
