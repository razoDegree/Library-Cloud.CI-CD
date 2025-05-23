import pytest
import requests

BASE_URL = "http://books:5001/books"

book = {
    "title": "Second Foundation",
    "ISBN": "9780553293364",
    "genre": "Science Fiction"
}

@pytest.fixture(scope="module")
def posted_book():
    res = requests.post(BASE_URL, json=book)
    assert res.status_code == 201
    return res.json()["ID"]

def test_get_book(posted_book):
    res = requests.get(f"{BASE_URL}/{posted_book}")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Second Foundation"

def test_delete_book(posted_book):
    res = requests.delete(f"{BASE_URL}/{posted_book}")
    assert res.status_code == 200

def test_get_deleted_book(posted_book):
    res = requests.get(f"{BASE_URL}/{posted_book}")
    assert res.status_code == 404
