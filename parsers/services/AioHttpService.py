import aiohttp

from docker.backend.config import PROXY_URL
from parsers.heders.copart_headers import COOKIES_FOR_JSON
from src.utils.logger import get_logger

logger = get_logger()


class AiohttpService:

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def get_json_data(
        self,
        url: str,
        proxy=True,
        cookies=True,
        **kwargs,
    ) -> dict | str | None:
        """Выполняет GET-запрос и возвращает JSON или текст"""
        session = await self.get_session()
        try:
            async with session.get(
                url,
                ssl=False,
                **kwargs,
                proxy=PROXY_URL if proxy else None,
                cookies=COOKIES_FOR_JSON if cookies else None,
            ) as response:
                logger.info(f"Aiohttp GET {url} -> {response.status}")
                return await response.json()
        except Exception as e:
            logger.warning(f"GET {url} failed: {e}")
            return {}

    async def get_cookies(self, url: str, **kwargs) -> dict | str | None:
        """Выполняет GET-запрос и возвращает куки"""
        session = await self.get_session()
        try:
            async with session.get(url, ssl=False, **kwargs) as r:
                logger.info(f"Aiohttp GET {url} -> {r.status}")
                return r.cookies
        except Exception as e:
            logger.warning(f"GET {url} failed: {e}")
            return None

    async def post_data(
        self, url: str, cookies, json_data, **kwargs
    ) -> dict | str | None:
        """Выполняет POST-запрос и возвращает JSON или текст"""
        session = await self.get_session()
        try:
            async with session.post(
                url, ssl=False, **kwargs, cookies=cookies, json=json_data
            ) as response:
                logger.info(f"Aiohttp POST {url} -> {response.status}")
                return await response.json()
        except Exception as e:
            logger.warning(f"POST {url} failed: {e}")
            return {}


aiohttp_service = AiohttpService()
