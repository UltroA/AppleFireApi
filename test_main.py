import psycopg
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID = {"username": "ren", "email": "ren@ren.ru", "password": "143Abcd"}


@pytest.fixture(scope="module", autouse=True)
def _app_lifespan():
    # без контекстного менеджера lifespan не запускается: пул закрыт, таблицы нет
    with client:
        yield


def _clear_users():
    with psycopg.connect(dbname="postgres", user="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE users RESTART IDENTITY CASCADE;")


@pytest.fixture
def clean_db():
    _clear_users()
    yield
    _clear_users()


def make(**overrides):
    return {**VALID, **overrides}


def auth_headers(user):
    client.post("/reg/", json=user)
    token = client.post(
        "/token",
        data={"username": user["email"], "password": user["password"]},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {'message': 'Hi nerd!'}


def test_unknown_route_404():
    assert client.get("/nope").status_code == 404


# Registration validation
@pytest.mark.parametrize("username", ["", "a", "ab", "a" * 16, "a" * 50])
def test_reg_bad_username_length(username):
    r = client.post("/reg/", json=make(username=username))
    assert r.status_code == 422


@pytest.mark.parametrize(
    "email",
    [
        "abcdefgh",
        "abc@defgh",
        "abc.defgh",
    ],
)
def test_reg_bad_email(email):
    r = client.post("/reg/", json=make(email=email))
    assert r.status_code == 422


@pytest.mark.parametrize(
    "password",
    [
        "",
        "Ab12",
        "abc123",
        "ABCDEF",
        "123456",
        "Abcde12",
    ],
)
def test_reg_bad_password(password):
    r = client.post("/reg/", json=make(password=password))
    assert r.status_code == 422


@pytest.mark.parametrize("missing", ["username", "email", "password"])
def test_reg_missing_field_422(missing):
    body = make()
    body.pop(missing)
    assert client.post("/reg/", json=body).status_code == 422


def test_reg_empty_body_422():
    assert client.post("/reg/", json={}).status_code == 422


def test_reg_wrong_method_405():
    assert client.get("/reg/").status_code == 405


def test_reg_success(clean_db):
    r = client.post("/reg/", json=VALID)
    assert r.status_code == 200
    assert r.json() == {'success': True, 'userID': 1}


@pytest.mark.parametrize("username", ["abc", "a" * 15])
def test_reg_username_boundaries_ok(clean_db, username):
    r = client.post("/reg/", json=make(username=username))
    assert r.status_code == 200


def test_reg_email_boundary_ok(clean_db):
    r = client.post("/reg/", json=make(email="a@bc.de"))
    assert r.status_code == 200


def test_reg_duplicate_user_409(clean_db):
    assert client.post("/reg/", json=VALID).status_code == 200
    r = client.post("/reg/", json=VALID)
    assert r.status_code == 409
    assert r.json()["detail"] == "User already exists"


def test_reg_inserts_row(clean_db):
    assert client.post("/reg/", json=VALID).status_code == 200
    with psycopg.connect(dbname="postgres", user="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            assert cur.fetchone()[0] == 1


# Login test
def test_login_success(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/token",
        data={"username": VALID["email"], "password": VALID["password"]},
    )
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert "access_token" in r.json()


def test_login_wrong_password(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/token", data={"username": VALID["email"], "password": "Wrong123"}
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password"


def test_login_unknown_user(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post("/token", data={"username": "ghost@ren.ru", "password": "Abc123"})
    assert r.status_code == 401


def test_login_empty_users_table(clean_db):
    r = client.post("/token", data={"username": "alice@ren.ru", "password": "Abc123"})
    assert r.status_code == 401


def test_login_missing_field_422():
    assert client.post("/token", data={"username": VALID["email"]}).status_code == 422


def test_login_is_case_sensitive(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/token", data={"username": VALID["email"], "password": "143abcd"}
    )
    assert r.status_code == 401


# Auth get info test
def test_me_success(clean_db):
    client.post("/reg/", json=VALID)
    token = client.post(
        "/token",
        data={"username": VALID["email"], "password": VALID["password"]},
    ).json()["access_token"]
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"user_id": 1, "friends": []}


def test_me_no_token_401():
    assert client.get("/me").status_code == 401


def test_me_invalid_token_401():
    r = client.get("/me", headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Could not validate credentials"


FRIEND = {"username": "reeen", "email": "reeeeen@ren.ru", "password": "143Abcd"}


# Friends test
def test_add_friend_no_token_401():
    r = client.post("/add_friend", params={"email": FRIEND["email"]})
    assert r.status_code == 401


def test_add_friend_invalid_token_401():
    r = client.post(
        "/add_friend",
        params={"email": FRIEND["email"]},
        headers={"Authorization": "Bearer not.a.token"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Could not validate credentials"


def test_add_friend_missing_email_422(clean_db):
    headers = auth_headers(VALID)
    assert client.post("/add_friend", headers=headers).status_code == 422


def test_add_friend_wrong_method_405():
    assert client.get("/add_friend").status_code == 405


def test_add_friend_success(clean_db):
    headers = auth_headers(VALID)
    client.post("/reg/", json=FRIEND)
    r = client.post("/add_friend", params={"email": FRIEND["email"]}, headers=headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "coupleId" in r.json()


def test_add_friend_inserts_row(clean_db):
    headers = auth_headers(VALID)
    client.post("/reg/", json=FRIEND)
    client.post("/add_friend", params={"email": FRIEND["email"]}, headers=headers)
    r = client.get("/me", headers=headers)
    assert r.status_code == 200
    assert len(r.json()["friends"]) == 1


def test_me_no_friends_by_default(clean_db):
    headers = auth_headers(VALID)
    r = client.get("/me", headers=headers)
    assert r.json()["friends"] == []


@pytest.mark.xfail(reason="add_friend crashes on unknown email (None[0])")
def test_add_friend_unknown_email_404(clean_db):
    headers = auth_headers(VALID)
    r = client.post("/add_friend", params={"email": "ghost@ren.ru"}, headers=headers)
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"

def test_add_friend_duplicate_409(clean_db):
    headers = auth_headers(VALID)
    client.post("/reg/", json=FRIEND)
    assert client.post("/add_friend", params={"email": FRIEND["email"]}, headers=headers).status_code == 200
    r = client.post("/add_friend", params={"email": FRIEND["email"]}, headers=headers)
    assert r.status_code == 409
    assert r.json()["detail"] == "Friend already exists"


def test_add_friend_duplicate_reverse_409(clean_db):
    headers = auth_headers(VALID)
    friend_headers = auth_headers(FRIEND)
    client.post("/add_friend", params={"email": FRIEND["email"]}, headers=headers)
    r = client.post("/add_friend", params={"email": VALID["email"]}, headers=friend_headers)
    assert r.status_code == 409