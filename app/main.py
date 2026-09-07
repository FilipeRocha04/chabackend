from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import admin, categories, gift_commitments, gift_items, lista_pessoas

# Creates tables that don't exist yet; it never alters or drops existing ones.
# Run db/schema.sql once for the initial setup (it also seeds the gift list).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chá da Maya API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(gift_items.router)
app.include_router(gift_commitments.router)
app.include_router(gift_commitments.totals_router)
app.include_router(admin.router)
app.include_router(lista_pessoas.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
