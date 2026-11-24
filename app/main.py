"""Small demo API used to showcase a production-style Kubernetes delivery pipeline."""

import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = os.getenv("APP_VERSION", "dev")
START_TIME = time.time()

app = FastAPI(title="demo-api", version=APP_VERSION)

_items: dict[int, dict] = {}
_next_id = 1


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)


class Item(ItemIn):
    id: int


@app.get("/healthz")
def healthz() -> dict:
    """Liveness probe: the process is up."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict:
    """Readiness probe: the app can serve traffic."""
    return {"status": "ready"}


@app.get("/version")
def version() -> dict:
    return {"version": APP_VERSION, "uptime_seconds": round(time.time() - START_TIME, 1)}


@app.get("/items", response_model=list[Item])
def list_items() -> list[dict]:
    return list(_items.values())


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemIn) -> dict:
    global _next_id
    record = {"id": _next_id, **item.model_dump()}
    _items[_next_id] = record
    _next_id += 1
    return record


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> dict:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="item not found")
    return _items[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    if _items.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail="item not found")


def reset_store() -> None:
    """Test helper: clear in-memory state."""
    global _next_id
    _items.clear()
    _next_id = 1
