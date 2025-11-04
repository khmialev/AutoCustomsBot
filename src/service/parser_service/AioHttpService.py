import aiohttp

from src.app.logger import get_logger
from src.app.settings import get_settings
from src.parsers.heders.CopartHeaders import COOKIES_FOR_JSON

logger = get_logger()
settings = get_settings()


class AiohttpService:

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None
        self._proxy = settings.get_proxy_url()

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
                proxy=self._proxy if self._proxy else None,
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
                url,
                ssl=False,
                **kwargs,
                cookies=cookies,
                json=json_data,
                proxy=self._proxy,
            ) as response:
                logger.info(f"Aiohttp POST {url} -> {response.status}")
                return await response.json()
        except Exception as e:
            logger.warning(f"POST {url} failed: {e}")
            return {}


aiohttp_service = AiohttpService()
