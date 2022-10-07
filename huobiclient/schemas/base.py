import base64
import datetime
import hashlib
import hmac
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode, urlparse

from pydantic import BaseModel, Field, root_validator

from huobiclient.config import huobi_client_config
from huobiclient.exceptions import HuobiError


def _utcnow() -> str:
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')


class BaseHuobiRequest(BaseModel):
    AccessKeyId: str = Field(default=huobi_client_config.HUOBI_ACCESS_KEY, const=True)
    SignatureMethod: str = Field(default='HmacSHA256', const=True)
    SignatureVersion: str = Field(default='2', const=True)
    Timestamp: str = Field(default_factory=_utcnow)
    Signature: Optional[str]

    def _calculate_hash(self, payload: str) -> str:
        digest = hmac.new(
            key=huobi_client_config.HUOBI_SECRET_KEY.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode()

    def sign(self, path: str, method: str) -> None:
        params = self.dict(exclude={'Signature'})
        payload = '%s\n%s\n%s\n%s' % (  # noqa:FS001
            method,
            urlparse(huobi_client_config.HUOBI_API_URL).hostname,
            path,
            urlencode(params),
        )
        self.Signature = self._calculate_hash(payload)

    def to_request(self, path: str, method: str, **kwargs: Any) -> Dict:
        self.sign(path, method)
        return self.dict(**kwargs)


class BaseHuobiResponse(BaseModel):
    status: str
    err_code: Optional[str] = Field(alias='err-code')
    err_msg: Optional[str] = Field(alias='err-msg')

    @root_validator
    def _check_error(cls, values: Dict[str, Union[str, Optional[str]]]) -> Dict:  # noqa:U100
        err_code = values.get('err_code', '') or ''
        err_msg = values.get('err_msg', '') or ''
        if values.get('status', '') != 'ok':
            raise HuobiError(
                err_code=err_code,
                err_msg=err_msg,
            )
        return values
