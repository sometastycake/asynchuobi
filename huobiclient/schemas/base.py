from typing import Dict, Optional, Union

from pydantic import BaseModel, Field, root_validator

from huobiclient.exceptions import HuobiError


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
