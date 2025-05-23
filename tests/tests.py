import requests

BASE_URL = "http://localhost:5000/books"

book = {
    "title": "1984",
    "ISBN": "9780451524935",
    "genre": "Dystopian"
}

def test_post_book():
    res = requests.post(BASE_URL, json=book)
    assert res.status_code == 201
    data = res.json()
    assert "ID" in data
    global book_id
    book_id = data["ID"]

def test_get_book():
    res = requests.get(f"{BASE_URL}/{book_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "1984"

def test_delete_book():
    res = requests.delete(f"{BASE_URL}/{book_id}")
    assert res.status_code == 200

def test_get_deleted_book():
    res = requests.get(f"{BASE_URL}/{book_id}")
    assert res.status_code == 404
