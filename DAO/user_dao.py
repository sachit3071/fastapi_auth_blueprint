from DAO.base_dao import BaseDAO
from models.models import User
from config.logging_config import log_function_call


class UserDAO(BaseDAO):
    @log_function_call
    def create_user(self, user_data: dict) -> User:
        return self.insert(User, user_data)

    @log_function_call
    async def get_user_by_filters(self, filters: dict) -> User | None:
        return await self.get_one(User, filters)

    @log_function_call
    async def update_user(self, filters: dict, user_data: dict) -> User | None:
        return await self.update(User, filters, user_data)

    @log_function_call
    async def add_user(self, user_data: dict) -> User | None:
        return await self.insert(User, user_data)
