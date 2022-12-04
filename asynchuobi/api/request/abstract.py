from abc import ABC, abstractmethod
from typing import Any


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def request(self, url: str, method: str, **kwargs: Any) -> Any:  # noqa:U100
        ...

    @abstractmethod
    async def get(self, url: str, **kwargs: Any) -> Any:  # noqa:U100
        ...

    @abstractmethod
    async def post(self, url: str, **kwargs: Any) -> Any:  # noqa:U100
        ...
