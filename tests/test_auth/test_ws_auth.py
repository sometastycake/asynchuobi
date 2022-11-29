def test_get_params_ws(ws_auth):
    params = ws_auth._get_params()
    assert params == {
        'accessKey': 'HUOBI_ACCESS_KEY',
        'param': 'param',
        'signatureMethod': 'HmacSHA256',
        'signatureVersion': '2.1',
        'timestamp': '2023-01-01T00:01:01'
    }


def test_calculate_hash_ws(ws_auth):
    result = ws_auth._calculate_hash('payload')
    assert result == 'zCNH2kCcoDGexM/IaZl+I8VIVWRS3YRGCgwTaH6Seho='


def test_sign_ws(ws_auth):
    result = ws_auth._sign(
        path='/path',
        method='GET',
        host='https://example.com',
    )
    assert result == '8RkCfP3ea3v2hhNRq6Ev5murwY5KAusypU/qRs//6hg='


def test_to_request_ws(ws_auth):
    result = ws_auth.to_request(
        url='https://example.com/path',
        method='GET',
    )
    assert result == {
        'accessKey': 'HUOBI_ACCESS_KEY',
        'authType': 'api',
        'param': 'param',
        'signature': 'haAcLquPMVYPwaGn3mzhtC1k/bXraIPNlUmgk34NDPY=',
        'signatureMethod': 'HmacSHA256',
        'signatureVersion': '2.1',
        'timestamp': '2023-01-01T00:01:01'
    }
