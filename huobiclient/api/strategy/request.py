from typing import Any, Optional

import aiohttp

from huobiclient.api.strategy.abstract import RequestStrategyAbstract


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

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
