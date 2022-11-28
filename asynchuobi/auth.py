import base64
import datetime
import hashlib
import hmac
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode, urlparse

from pydantic import BaseModel, Field


def _utcnow() -> str:
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')


def _parse_url(url: str) -> Tuple[Optional[str], str]:
    parsed = urlparse(url)
    return parsed.hostname, parsed.path


class _BaseAuth(BaseModel):
    SecretKey: str
    Signature: Optional[str]

    def _calculate_hash(self, payload: str) -> str:
        digest = hmac.new(
            key=self.SecretKey.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode()

    def _get_params(self) -> Dict:
        return self.dict(
            exclude={
                'Signature',
                'SecretKey',
            },
            exclude_none=True,
            by_alias=True,
        )

    def _sign(self, path: str, method: str, host: str) -> str:
        params = self._get_params()
        payload = '\n'.join([method, host, path, urlencode(params)])
        return self._calculate_hash(payload)

    def to_request(self, url: str, method: str) -> Dict:
        host, path = _parse_url(url)
        if host is None:
            raise ValueError('Host cannot be None')
        self.Signature = self._sign(path, method, host)
        return self.dict(
            exclude_none=True,
            by_alias=True,
            exclude={'SecretKey'},
        )


class APIAuth(_BaseAuth):
    AccessKeyId: str
    SignatureMethod: str = Field(default='HmacSHA256', const=True)
    SignatureVersion: str = Field(default='2', const=True)
    Timestamp: str = Field(default_factory=_utcnow)


class WebsocketAuth(_BaseAuth):
    authType: str = Field(default='api', const=True)
    accessKey: str
    signatureMethod: str = Field(default='HmacSHA256', const=True)
    signatureVersion: str = Field(default='2.1', const=True)
    timestamp: str = Field(default_factory=_utcnow)
    signature: Optional[str]

    def _get_params(self) -> Dict:
        return self.dict(
            exclude={
                'signature',
                'SecretKey',
                'authType',
            },
            exclude_none=True,
            by_alias=True,
        )

    def to_request(self, url: str, method: str) -> Dict:
        host, path = _parse_url(url)
        if host is None:
            raise ValueError('Host cannot be None')
        self.signature = self._sign(path, method, host)
        return self.dict(
            exclude_none=True,
            by_alias=True,
            exclude={'SecretKey'},
        )
