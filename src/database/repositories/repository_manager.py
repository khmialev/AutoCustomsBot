from src.database.repositories.manager import OrmRepositoryManager
from src.database.repositories.tracking_repository import TrackingRepository
from src.database.repositories.user_repository import UserRepository


class RepositoryManager(OrmRepositoryManager):
    async def __aenter__(self):
        # создаём конкретные репозитории
        self.users = UserRepository(self._session)
        self.tracking = TrackingRepository(self._session)
        return self
