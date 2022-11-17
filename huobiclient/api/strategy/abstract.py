from abc import ABC, abstractmethod
from typing import Any


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def request(self, url: str, method: str, **kwargs: Any) -> Any:  # noqa:U100
        ...
