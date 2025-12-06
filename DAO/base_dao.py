from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, distinct, update
from typing import Type, Optional, Any


class BaseDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, model: Type[Any], data: dict) -> Any:
        instance = model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def bulk_insert(self, model: Type[Any], data_list: list[dict]) -> list[Any]:
        instances = [model(**data) for data in data_list]
        self.session.add_all(instances)
        await self.session.commit()
        return instances

    async def bulk_upsert(
        self, model: Type[Any], data_list: list[dict], conflict_columns: list[str]
    ) -> list[Any]:
        if not data_list:
            return []

        stmt = insert(model).values(data_list)
        update_cols = {
            c.name: c for c in stmt.excluded if c.name not in conflict_columns
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_cols
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return data_list

    async def get_all(
        self,
        model: Type[Any],
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
    ) -> list[Any]:
        stmt = select(model)

        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(model, key) == value)

        if order_by:
            stmt = stmt.order_by(getattr(model, order_by))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_one(
        self, model: Type[Any], filters: Optional[dict] = None
    ) -> Optional[Any]:
        stmt = select(model)

        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(model, key) == value)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, model: Type[Any], filters: dict) -> None:
        stmt = delete(model)

        for key, value in filters.items():
            stmt = stmt.where(getattr(model, key) == value)

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_distinct(self, model: Type[Any], column_name: str) -> list[Any]:
        column = getattr(model, column_name)
        stmt = select(distinct(column))

        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def update(self, model: Type[Any], filters: dict, data: dict) -> None:
        for key, val in filters.items():
            stmt = update(model).where(getattr(model, key) == val).values(data)
        await self.session.execute(stmt)
        await self.session.commit()
