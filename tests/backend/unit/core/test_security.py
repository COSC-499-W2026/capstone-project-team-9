from core.security import hash_password, verify_password


def test_hash_password():
    password = "hashed_password_1"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$12$")
    assert verify_password(password, hashed)


def test_hash_password_uses_different_salts():
    password = "hashed_password_1"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-password")

    assert not verify_password("wrong-password", hashed)
