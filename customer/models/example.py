from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class ExampleItemBase(SQLModel):
    name: str


class ExampleItem(ExampleItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ExampleItemCreate(ExampleItemBase):
    pass

