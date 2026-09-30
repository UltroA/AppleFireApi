import psycopg
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID = {"username": "ren", "email": "ren@ren.ru", "password": "143Abcd"}


def _drop_users():
    with psycopg.connect(dbname="postgres", user="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS users;")


@pytest.fixture
def clean_db():
    _drop_users()
    yield
    _drop_users()


def make(**overrides):
    return {**VALID, **overrides}


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == ["Hi nerd!"]


def test_unknown_route_404():
    assert client.get("/nope").status_code == 404


# Registration validation
@pytest.mark.parametrize("username", ["", "a", "ab", "a" * 16, "a" * 50])
def test_reg_bad_username_length(username):
    r = client.post("/reg/", json=make(username=username))
    assert r.status_code == 413


@pytest.mark.parametrize(
    "email",
    [
        "a@b.c",
        "abcdefgh",
        "abc@defgh",
        "abc.defgh",
        "a" * 30 + "@b.com",
    ],
)
def test_reg_bad_email(email):
    r = client.post("/reg/", json=make(email=email))
    assert r.status_code == 413


@pytest.mark.parametrize(
    "password",
    [
        "",
        "Ab12",
        "abc123",
        "ABCDEF",
        "123456",
        "Ab1234",
        "Abcde12",
    ],
)
def test_reg_bad_password(password):
    r = client.post("/reg/", json=make(password=password))
    assert r.status_code == 413


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
    assert r.json() == [True]


@pytest.mark.parametrize("username", ["abc", "a" * 15])
def test_reg_username_boundaries_ok(clean_db, username):
    r = client.post("/reg/", json=make(username=username))
    assert r.status_code == 200


def test_reg_email_boundary_ok(clean_db):
    r = client.post("/reg/", json=make(email="a@bc.de"))
    assert r.status_code == 200


def test_reg_duplicate_user_400(clean_db):
    assert client.post("/reg/", json=VALID).status_code == 200
    r = client.post("/reg/", json=VALID)
    assert r.status_code == 400
    assert r.json()["detail"] == "User already exists"


def test_reg_creates_table_if_missing(clean_db):
    assert client.post("/reg/", json=VALID).status_code == 200
    with psycopg.connect(dbname="postgres", user="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            assert cur.fetchone()[0] == 1


# Login test
def test_login_success(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/login/",
        json={"username": VALID["username"], "password": VALID["password"]},
    )
    assert r.status_code == 200
    assert r.json() == [True]


def test_login_wrong_password(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/login/", json={"username": VALID["username"], "password": "Wrong123"}
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Wrong username or password"


def test_login_unknown_user(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post("/login/", json={"username": "ghost", "password": "Abc123"})
    assert r.status_code == 403


def test_login_no_users_table(clean_db):
    # table does not exist -> query fails -> still a clean 403, not a 500
    r = client.post("/login/", json={"username": "alice", "password": "Abc123"})
    assert r.status_code == 403


def test_login_missing_field_422():
    assert client.post("/login/", json={"username": "alice"}).status_code == 422


def test_login_is_case_sensitive(clean_db):
    client.post("/reg/", json=VALID)
    r = client.post(
        "/login/", json={"username": VALID["username"], "password": "abc123"}
    )
    assert r.status_code == 403
