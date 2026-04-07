from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_tables
from app.api import users, inventory, plans, shopping


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: create tables (dev only — use Alembic in prod)
    if settings.app_env == "development":
        await create_tables()
    yield
    # On shutdown: nothing needed for SQLite; add connection pool teardown for Postgres


app = FastAPI(
    title="Meal Planner API",
    description="Constraint-aware, stateful meal planning agent.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(plans.router)
app.include_router(shopping.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.app_env}
