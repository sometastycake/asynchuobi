from typing import Any, Optional

import aiohttp

from asynchuobi.api.strategy.abstract import RequestStrategyAbstract


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._session: Optional[aiohttp.ClientSession] = None

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _create_session(self) -> aiohttp.ClientSession:
        kwargs = self._kwargs
        if 'connector' not in kwargs:
            kwargs['connector'] = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(**kwargs)

    async def request(self, url: str, method: str, **kwargs: Any) -> Any:
        if self._session is None:
            self._session = self._create_session()
        response = await self._session.request(
            url=url,
            method=method,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers={
                'Content-Type': 'application/json',
            },
        )
        return await response.json()
