from libraryFunctions.Private import genai_key
from libraryFunctions.Book import Book
import requests
import google.generativeai as genai  # Gemini API Library


class BooksCollection:
    """
    A class to manage a collection of Book objects, allowing creation, retrieval, update,
    deletion, and filtering of books using external APIs for metadata enrichment.
    """

    def __init__(self):
        """
        Initializes an empty collection of books.

        Attributes:
            num_of_books (int): Total number of books in the collection.
            books (list): List that holds Book objects.
        """
        self.books = []

    def createNewBook(self, title, ISBN, genre):
        """
        Creates a new Book object using metadata from Google Books, OpenLibrary, and Gemini APIs.

        Args:
            title (str): Title of the book.
            ISBN (str): ISBN identifier of the book.
            genre (str): Genre of the book.

        Returns:
            Book: A Book object with populated data.
            dict: Error message if data retrieval fails.
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

        authors_list = google_books_data.get("authors", ["missing"])
        authors = " and ".join(authors_list)

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
        Retrieves a Book object from the collection by ID.

        Args:
            id (str or int): The ID of the book to retrieve.

        Returns:
            Book: The requested Book object.
            dict: Error message if book not found.
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
        Deletes a Book object from the collection by ID.

        Args:
            id (str or int): The ID of the book to delete.

        Returns:
            dict: Success or error message.
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
        Updates fields of an existing Book object.

        Args:
            book_data (dict): Dictionary of field names and new values.
            id (str or int): The ID of the book to update.

        Returns:
            dict: Success or error message.
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
        Updates fields of an existing Book object.

        Args:
            book_data (dict): Dictionary of field names and new values.
            id (str or int): The ID of the book to update.

        Returns:
            dict: Success or error message.
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
        Retrieves all books that match given filter criteria.

        Args:
            filters (dict): Dictionary of field-value pairs to filter the books (e.g. {"genre": "fiction"}).

        Returns:
            list: A list of books (in JSON form) matching the filter.
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
