import pytest
import requests

BASE_URL = "http://localhost:5001/books"

book = {
    "title": "Second Foundation",
    "ISBN": "9780553293364",
    "genre": "Science Fiction"
}


def test_get_books():
    res = requests.get(f"{BASE_URL}")
    assert res.status_code == 200
    
def test_posted_book():
    res = requests.post(BASE_URL, json=book)
    assert res.status_code == 201
    return res.json()["book_id"]

def test_get_book():
    res = requests.get(f"{BASE_URL}/{book['ISBN']}")
    assert res.status_code == 202
    data = res.json()
    assert data["title"] == "Second Foundation"

def test2_delete_book():
    res = requests.delete(f"{BASE_URL}/{book['ISBN']}")
    assert res.status_code == 200

def test_get_deleted_book():
    res = requests.get(f"{BASE_URL}/{book['ISBN']}")
    assert res.status_code == 404
