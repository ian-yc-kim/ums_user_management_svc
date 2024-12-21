import pytest
import datetime
from src.ums_user_management_svc.utils.jwt import generate_token, validate_token


def test_generate_token():
    payload = {'user_id': 1}
    token = generate_token(payload)
    assert isinstance(token, str)


def test_validate_token_success():
    payload = {'user_id': 1}
    token = generate_token(payload)
    decoded = validate_token(token)
    assert decoded['user_id'] == 1
    assert 'exp' in decoded


def test_validate_token_expired():
    payload = {'user_id': 2}
    token = generate_token(payload, expires_delta=datetime.timedelta(seconds=-1))
    with pytest.raises(Exception) as e:
        validate_token(token)


def test_validate_token_invalid():
    invalid_token = 'invalid.token.string'
    with pytest.raises(Exception) as e:
        validate_token(invalid_token)