import hashlib
import json
import os
import time
from jwcrypto import jwe, jwk
from jwcrypto.common import JWException, base64url_encode

ACCESS_TOKEN_EXPIRE_SECONDS = 1800


def _token_secret() -> bytes:
    secret = os.getenv("AUTH_TOKEN_SECRET")
    if not secret or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_TOKEN_SECRET must be set to at least 32 characters.")
    return secret.encode("utf-8")


def _token_key(secret: bytes) -> jwk.JWK:
    key = hashlib.sha256(secret).digest()
    return jwk.JWK(kty="oct", k=base64url_encode(key))


def create_access_token(user_id: int) -> str:
    token = jwe.JWE(
        plaintext=json.dumps(
            {
                "sub": str(user_id),
                "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
            },
            separators=(",", ":"),
        ),
        protected={"alg": "dir", "enc": "A256GCM", "typ": "JWT"},
    )
    token.add_recipient(_token_key(_token_secret()))
    return token.serialize(compact=True)


def decode_access_token(token: str) -> int | None:
    secret = _token_secret()
    try:
        encrypted_token = jwe.JWE()
        encrypted_token.deserialize(token, key=_token_key(secret))
        header = encrypted_token.jose_header
        if (
            header.get("alg") != "dir"
            or header.get("enc") != "A256GCM"
            or header.get("typ") != "JWT"
        ):
            return None

        payload = json.loads(encrypted_token.payload)
        user_id = int(payload["sub"])
        expires_at = int(payload["exp"])
        if user_id <= 0 or expires_at <= time.time():
            return None
        return user_id
    except (JWException, KeyError, TypeError, ValueError, UnicodeDecodeError):
        return None
