from libraryFunctions.Private import genai_key
from libraryFunctions.Book import Book
import requests
import google.generativeai as genai  # Gemini API Library


class BooksCollection:
    # Books Collection Constructor
    def __init__(self):
        self.num_of_books = 0
        self.books = []

    def createNewBook(self, title, ISBN, genre):
        """
        Creating new Book object

        return:
            Book Object
        """
        # Getting the authors, publisher, publishedDate from Google Books API
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}"
        google_books_response = requests.get(google_books_url)
        try:
            google_books_data = google_books_response.json()["items"][0][
                "volumeInfo"
            ]  # Extracting the information about the book
        except:
            if google_books_response.json()["totalItems"] == 0:
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

        # Getting the language from OpenLibrary API
        openLibary_url = f"https://openlibrary.org/search.json?q={ISBN}&fields=key,title,author_name,language"
        openLibary_response = requests.get(openLibary_url)
        try:
            openLibary_data = openLibary_response.json()["docs"][0]
        except:
            if openLibary_response.json()["numFound"] == 0:
                return {
                    "Error": f"No answer returnd from OpenLibrary API for ISBN num: {ISBN}"
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
            return {"Error": f"No answer returned from GEMINI for ISBN num: {ISBN}"}

        summary = "missing" if response.text is None else response.text

        # Need to create based on some calculation
        id = str(ISBN)

        newBook = Book(
            title, authors, ISBN, publisher, publishedDate, genre, language, summary, id
        )
        return newBook

    def getBook(self, id):
        """
        GET /books/{id} request: Getting book id, return it from the list of the books

        return:
            Book Object
        """
        asked_book = next(
            (book for book in self.books if str(book.id) == str(id)), None
        )
        if asked_book != None:
            return asked_book
        else:
            return {"Error": f"No Books Exists with id: {id}"}

    def deleteBook(self, id):
        """
        DELETE /books/{id} request: Getting book id, delete it from the list of the books
        """
        try:
            book_to_delete = next(
                (book for book in self.books if book.id == str(id)), None
            )
            self.books.remove(book_to_delete)
        except:
            return {"Error": f"No Books Exists with id: {id}"}

        self.num_of_books -= 1
        return {"Success": f"Book {id} deleted Successefully"}

    def changeBook(self, book_data, id):
        """
        PUT /books/{id} request: Getting book data and book id and update the book data
        """

        # Check if the Book exists
        update_book = self.getBook(id)
        if not isinstance(update_book, Book):
            return update_book

        # Check if the fields are valid
        for field, value in book_data.items():
            if not hasattr(update_book, field):
                return {"Error": f"Field {field} is not a book field"}

        # Update the values
        for field, value in book_data.items():
            setattr(update_book, field, value)

        return {"Success": f"Book {update_book.id} updated successfully."}

    def addBook(self, title, ISBN, genre):
        """
        POST /books request: Getting title, ISBN-13, genre of a book and add a new book to the list of books

        return:
            new Book id as String
        """
        new_book = self.createNewBook(title, ISBN, genre)

        if not isinstance(new_book, Book):
            return new_book["Error"]
        else:
            self.books.append(new_book)
            self.num_of_books += 1

        return new_book.id

    def getBooksCollection(self, filters={}):
        """
        GET /books requst: Getting fields and values and return list of all the books corresponeding to the values of the fields
        filters = {'id': '1', 'publisher': 'smile'} example
        """

        requested_books = []

        for book in self.books:
            match = True
            for field, value in filters.items():
                if not hasattr(book, field):
                    match = False
                    break

                field_value = getattr(book, field)

                # If it's a list → check if value is in it
                if isinstance(field_value, list):
                    if value not in field_value:
                        match = False
                        break
                else:
                    # Regular value → check exact match
                    if str(field_value) != str(value):
                        match = False
                        break

            if match:
                requested_books.append(book.toJson())

        return requested_books
