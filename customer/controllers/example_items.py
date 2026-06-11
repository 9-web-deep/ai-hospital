from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models.example import ExampleItem, ExampleItemCreate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ExampleItem)
def create_item(
    payload: ExampleItemCreate,
    session: Session = Depends(get_session),
) -> ExampleItem:
    item = ExampleItem(name=payload.name)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("", response_model=list[ExampleItem])
def list_items(session: Session = Depends(get_session)) -> list[ExampleItem]:
    return list(session.exec(select(ExampleItem)))
