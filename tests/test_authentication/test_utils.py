import re

from asynchuobi.auth import _parse_url, _utcnow  # noqa


def test_parse_url():
    host, path = _parse_url('https://example.com/path')
    assert host == 'example.com'
    assert path == '/path'


def test_utcnow():
    now_ = _utcnow()
    assert isinstance(now_, str)
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', now_)
