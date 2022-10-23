import base64
import datetime
import hashlib
import hmac
from typing import Dict, Optional
from urllib.parse import urlencode, urlparse

from pydantic import BaseModel, Field

from huobiclient.config import huobi_client_config as cfg


def _utcnow() -> str:
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')


def _calculate_hash(payload: str) -> str:
    digest = hmac.new(
        key=cfg.HUOBI_SECRET_KEY.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


class APIAuth(BaseModel):
    AccessKeyId: str = Field(default=cfg.HUOBI_ACCESS_KEY, const=True)
    SignatureMethod: str = Field(default='HmacSHA256', const=True)
    SignatureVersion: str = Field(default='2', const=True)
    Timestamp: str = Field(default_factory=_utcnow)
    Signature: Optional[str]

    def _sign(self, path: str, method: str, api_url: str) -> str:
        params = self.dict(
            exclude={
                'Signature',
            },
            exclude_none=True,
            by_alias=True,
        )
        payload = '%s\n%s\n%s\n%s' % (  # noqa:FS001
            method,
            urlparse(api_url).hostname,
            path,
            urlencode(params),
        )
        return _calculate_hash(payload)

    def to_request(self, path: str, method: str) -> Dict:
        self.Signature = self._sign(
            path=path,
            method=method,
            api_url=cfg.HUOBI_API_URL,
        )
        return self.dict(exclude_none=True, by_alias=True)


class WebsocketAuth(BaseModel):
    authType: str = Field(default='api', const=True)
    accessKey: str = Field(default=cfg.HUOBI_ACCESS_KEY, const=True)
    signatureMethod: str = Field(default='HmacSHA256', const=True)
    signatureVersion: str = Field(default='2.1', const=True)
    timestamp: str = Field(default_factory=_utcnow)
    signature: Optional[str]

    def _sign(self, path: str, method: str, api_url: str) -> str:
        params = self.dict(
            exclude={
                'signature',
                'authType'
            },
            exclude_none=True,
            by_alias=True,
        )
        payload = '%s\n%s\n%s\n%s' % (  # noqa:FS001
            method,
            urlparse(api_url).hostname,
            path,
            urlencode(params),
        )
        return _calculate_hash(payload)

    def to_request(self) -> Dict:
        self.signature = self._sign(
            path='/ws/v2',
            method='GET',
            api_url=cfg.HUOBI_WS_ASSET_AND_ORDER_URL,
        )
        return self.dict(exclude_none=True, by_alias=True)
