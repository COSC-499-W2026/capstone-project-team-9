import pytest
from models import User
from repositories.user_repo import (
    get_user_by_email,
    get_all_users,
    get_user_by_name,
    create_user,
    DuplicateUserError,
)


def test_get_all_users_by_email(session):
    user1 = User(
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )
    user2 = User(
        name="Bob",
        email="bob@example.com",
        hashed_password="hashed_password_2",
    )

    session.add_all([user1, user2])
    session.commit()

    alice = get_user_by_email(session, "alice@example.com")
    bob = get_user_by_email(session, "bob@example.com")

    assert alice is not None
    assert alice.name == "Alice"
    assert alice.email == "alice@example.com"

    assert bob is not None
    assert bob.name == "Bob"
    assert bob.email == "bob@example.com"


def test_get_all_users(session):
    user1 = User(
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )
    user2 = User(
        name="Bob",
        email="bob@example.com",
        hashed_password="hashed_password_2",
    )

    session.add_all([user1, user2])
    session.commit()

    user_list = get_all_users(session)

    assert user_list is not None
    assert len(user_list) == 2

    assert user_list[0].name == "Alice"
    assert user_list[0].email == "alice@example.com"

    assert user_list[1].name == "Bob"
    assert user_list[1].email == "bob@example.com"


def test_get_all_users_empty_table(session):
    assert get_all_users(session) == []


def test_get_users_by_name(session):
    user1 = User(
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )
    user2 = User(
        name="Bob",
        email="bob@example.com",
        hashed_password="hashed_password_2",
    )
    
    session.add_all([user1, user2])
    session.commit()
    
    alice = get_user_by_name(session, "Alice")
    bob = get_user_by_name(session, "Bob")

    assert alice is not None
    assert alice.name == "Alice"
    assert alice.email == "alice@example.com"
    
    assert bob is not None
    assert bob.name == "Bob"
    assert bob.email == "bob@example.com"


def test_create_user(session):
    user = create_user(
        session,
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )

    assert user is not None
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.hashed_password == "hashed_password_1"

def test_create_user_duplicate_email(session):
    create_user(
        session,
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )

    with pytest.raises(DuplicateUserError):
        create_user(
            session,
            name="Bob",
            email="alice@example.com",
            hashed_password="hashed_password_2",
        )


def test_create_user_duplicate_name(session):
    create_user(
        session,
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_password_1",
    )

    with pytest.raises(DuplicateUserError):
        create_user(
            session,
            name="Alice",
            email="alice2@example.com",
            hashed_password="hashed_password_2",
        )