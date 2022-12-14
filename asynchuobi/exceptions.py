class HuobiError(Exception):

    def __init__(self, err_code: str, err_msg: str):
        self.err_code = err_code
        self.err_msg = err_msg

    def __str__(self) -> str:
        return f'Error code "{self.err_code}" with message "{self.err_msg}"'


class WSHuobiError(HuobiError):
    ...


class WSNotAuthenticated(Exception):
    ...


class WSAuthenticateError(WSHuobiError):
    ...
