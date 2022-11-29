def test_get_params(api_auth):
    params = api_auth._get_params()
    assert params == {
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'param': 'param'
    }


def test_calculate_hash(api_auth):
    result = api_auth._calculate_hash('payload')
    assert result == 'zCNH2kCcoDGexM/IaZl+I8VIVWRS3YRGCgwTaH6Seho='


def test_sign(api_auth):
    result = api_auth._sign(
        path='/path',
        method='GET',
        host='https://example.com',
    )
    assert result == '95Xq4vTI2E4TplHZ6mQXafBtVBUF0ZfsnsXbJllYOdc='


def test_to_request(api_auth):
    result = api_auth.to_request(
        url='https://example.com/path',
        method='GET',
    )
    assert result == {
        'Signature': 'vGITXZ82gm+2tQEmYTzc9aQNWBlZUYZ8V1fY9nEKstI=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'param': 'param',
    }
