from src.database.repositories.absctract_repository import AbstractRepository
from src.database.models import UserModel


class UserRepository(AbstractRepository[UserModel]):
    """
    Репозиторий для таблицы users.
    Наследуется от AbstractRepository и получает готовые CRUD методы.
    """

    def __init__(self, session):
        super().__init__(session, UserModel)

    async def get_by_user_id(self, user_id: int):
        """Найти пользователя по Telegram user_id"""
        return await self.get(user_id=user_id)
