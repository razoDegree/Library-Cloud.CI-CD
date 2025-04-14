from libraryFunctions.Private import genai_key
from libraryFunctions.Book import Book
import requests
import google.generativeai as genai  # Gemini API Library

class BooksCollection:
    # Books Collection Constructor
    def __init__(self):
        self.num_of_books = 0
        self.books = []
        # self.top3 = [] # Holds the indexs of the top 3 books

    # Creating new book object
    def createNewBook(self, title, ISBN, genre):
        # Getting the authors, publisher, publishedDate from Google Books API
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}"
        google_books_response = requests.get(google_books_url)
        try:
            google_books_data = google_books_response.json()["items"][0][
                "volumeInfo"
            ]  # Extracting the information about the book
        except:
            if google_books_response.json()["totalItems"] == 0:
                print("ERROR")
                return {
                    "Error": f"No Items Returnd from Google Books API for this {ISBN}"
                }

        authors = (
            "missing"
            if google_books_data.get("authors") is None
            else google_books_data.get("authors")
        )
        publisher = (
            "missing"
            if google_books_data.get("publisher") is None
            else google_books_data.get("publisher")
        )
        publishedDate = (
            "missing"
            if google_books_data.get("publishedDate") is None
            else google_books_data.get("publishedDate")
        )
        genre = (
            "missing"
            if google_books_data.get("categories") is None
            else google_books_data.get("categories")
        )

        # Getting the language from OpenLibrary API
        openLibary_url = f"https://openlibrary.org/search.json?q={ISBN}&fields=key,title,author_name,language"
        openLibary_response = requests.get(openLibary_url)
        try:
            openLibary_data = openLibary_response.json()["docs"][0]
        except:
            if openLibary_response.json()["numFound"] == 0:
                return {
                    "Error": f"No Items Returnd from OpenLibrary API for this {ISBN}"
                }

        language = (
            ["missing"]
            if openLibary_data.get("language") is None
            else openLibary_data.get("language")
        )

        # Getting the summary from Gemini API
        genai.configure(api_key=genai_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        try:
            response = model.generate_content(
                f'Summarize the book "{title}" by {authors} in 5 sentences or less.'
            )
        except:
            return {"Error": f"NO ANSWERED RETURNED FROM GEMINI for this {ISBN}"}

        summary = "missing" if response.text is None else response.text

        # Need to create based on some calculation
        id = ISBN

        newBook = Book(
            title, authors, ISBN, publisher, publishedDate, genre, language, summary, id
        )
        return newBook

    # GET /books/{id} request: Getting book id, return it from the list of the books
    def getBook(self, id):
        try:
            asked_book = next((book for book in self.books if book.id == id), None)
            if asked_book != None:
                return asked_book.toJson(), 201
        except:
            return {"Error": f"No Books Exists with id: {id}"}

    # DELETE /books/{id} request: Getting book id, delete it from the list of the books
    def deleteBook(self, id):
        try:
            book_to_delete = next((book for book in self.books if book.id == id), None)
            self.books.remove(book_to_delete)
        except:
            return {"Error": f"No Books Exists with id: {id}"}

        self.num_of_books -= 1
        print(f"Book {id} Deleted Successefully.")

    # PUT /books/{id} request: Getting book
    def changeBook(self, BookJSON):
        return

    # POST /books request: Getting title, ISBN-13, genre of a book and add a new book to the list of books
    def addBook(self, title, ISBN, genre):
        new_book = self.createNewBook(title, ISBN, genre)
        self.books.append(new_book)
        self.num_of_books += 1

        print(f"Book added successfully | {new_book.id}")
        return new_book.id

    # GET /books requst: Getting fields and values and return list of all the books corresponeding to the values of the fields
    # The function assumes the fields names are valides (need to be checked in the request handling function!!)
    def getBooksCollection(self, filters={}):
        # filters = {'id': '1', 'publisher': 'smile'} example
        requested_books = []

        for book in self.books:
            match = True
            for field, value in filters.items():
                if str(getattr(book, field, None)) != str(value):
                    match = False
                    break
            requested_books.append(book.toJson()) if match else None

        return requested_books
