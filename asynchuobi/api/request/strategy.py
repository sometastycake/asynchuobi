from typing import Any, Optional

import aiohttp

from asynchuobi.api.request.abstract import RequestStrategyAbstract


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self, **session_kwargs: Any):
        self._session_kwargs = session_kwargs
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session and self._session.connector:
            if not self._session.connector.closed:
                self._session.connector.close()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _create_session(self) -> aiohttp.ClientSession:
        kwargs = self._session_kwargs
        if 'connector' not in kwargs:
            kwargs['connector'] = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(**kwargs)

    async def request(self, url: str, method: str, **kwargs: Any) -> Any:
        if self._session is None:
            self._session = self._create_session()
        response = await self._session.request(
            url=url,
            method=method,
            **kwargs,
        )
        return await response.json()

    async def get(self, url: str, **kwargs: Any) -> Any:
        return await self.request(url=url, method='GET', **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Any:
        return await self.request(url=url, method='POST', **kwargs)
