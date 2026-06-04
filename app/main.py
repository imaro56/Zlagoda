from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import pool
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()

app = FastAPI(name="Zlagoda", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
