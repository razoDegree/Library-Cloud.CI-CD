# import pytest
# import connectionController
# import requests
# import json
# #from connectionController import http_post, http_get, http_delete
# from assertions import assert_status_code, assert_field

# # Test data for books
# books = [
#     {"title": "Adventures of Huckleberry Finn", "ISBN": "9780520343641", "genre": "Fiction"},
#     {"title": "The Best of Isaac Asimov", "ISBN": "9780385050784", "genre": "Science Fiction"},
#     {"title": "Fear No Evil", "ISBN": "9780394558783", "genre": "Biography"},
#     {"title": "No such book", "ISBN": "0000001111111", "genre": "Biography"},
#     {"title": "The Greatest Joke Book Ever", "authors": "Mel Greene", "ISBN": "9780380798490", "genre": "Jokes"}
# ]

# ids = []

# # Test 1: Post books and check for unique IDs and correct status code
# @pytest.mark.parametrize("book", books[:3])
# def test_post_books_unique_ids(book):
#     response = connectionController.http_post("books", book)
#     assert_status_code(response, 201)
#     book_id = response.json()["ID"]
#     assert book_id not in ids, "Duplicate ID found"
#     ids.append(book_id)

# # Test 2: Get book by ID
# def test_get_book_by_id():
#     response = connectionController.http_get(f"books/{ids[0]}")
#     assert_status_code(response, 200)
#     assert_field(response, 'authors', 'Mark Twain')

# # Test 3: Get all books
# def test_get_all_books():
#     response = connectionController.http_get("books")
#     assert_status_code(response, 200)
#     assert len(response.json()) == 3, "Incorrect number of books returned"

# # Test 4: Post invalid book ISBN
# def test_post_invalid_book_isbn():
#     response = connectionController.http_post("books", books[3])
#     assert_status_code(response, 500)

# # Test 5: Delete a book
# def test_delete_book():
#     response = connectionController.http_delete(f"books/{ids[1]}")
#     assert_status_code(response, 200)

# # Test 6: Get deleted book
# def test_get_deleted_book():
#     response = connectionController.http_get(f"books/{ids[1]}")
#     assert_status_code(response, 404)

# # Test 7: Post book with unacceptable genre
# def test_post_unacceptable_genre():
#     response = connectionController.http_post("books", books[4])
#     assert_status_code(response, 422)

# ----- NIR TEST ------ 

import requests

BASE_URL = "http://localhost:5000/books"

book6 = {
    "title": "The Adventures of Tom Sawyer",
    "ISBN": "9780195810400",
    "genre": "Fiction"
}

book7 = {
    "title": "I, Robot",
    "ISBN": "9780553294385",
    "genre": "Science Fiction"
}

book8 = {
    "title": "Second Foundation",
    "ISBN": "9780553293364",
    "genre": "Science Fiction"
}

books_data = []


def test_post_books():
    books = [book6, book7, book8]
    for book in books:
        res = requests.post(BASE_URL, json=book)
        assert res.status_code == 201
        res_data = res.json()
        assert "ID" in res_data
        books_data.append(res_data)
        books_data_tuples = [frozenset(book.items()) for book in books_data]
    assert len(set(books_data_tuples)) == 3


