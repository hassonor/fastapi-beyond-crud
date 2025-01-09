from datetime import timedelta
from src.auth.utils import (
    generate_passwd_hash,
    verify_password,
    create_access_token,
    decode_token
)


def test_generate_passwd_hash():
    plain_pw = "secret123"
    hashed = generate_passwd_hash(plain_pw)
    assert hashed != plain_pw
    assert hashed.startswith("$2b$")


def test_verify_password():
    plain_pw = "secret123"
    hashed = generate_passwd_hash(plain_pw)
    assert verify_password(plain_pw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    token = create_access_token({"email": "test@example.com"})
    assert isinstance(token, str)


def test_decode_token_valid():
    token = create_access_token({"email": "test@example.com"})
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["user"]["email"] == "test@example.com"


def test_decode_token_invalid():
    invalid = "random.token.payload"
    decoded = decode_token(invalid)
    assert decoded is None


def test_decode_token_expired():
    token = create_access_token({"email": "test@example.com"}, expiry=timedelta(seconds=-1))
    decoded = decode_token(token)
    assert decoded is None
