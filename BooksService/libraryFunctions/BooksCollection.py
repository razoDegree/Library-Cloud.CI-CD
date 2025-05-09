from libraryFunctions.Private import genai_key
import requests
import google.generativeai as genai  # Gemini API Library
from pymongo import MongoClient



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

        uri = "mongodb://mongo:27017/"
        self.client = MongoClient(uri)
        self.database = self.client["library"]
        self.books_col = self.database["books_collection"]

    def createNewBook(self, title, ISBN, genre):
        """
        Creates a new Book document using metadata from Google Books, OpenLibrary, and Gemini APIs.

        Args:
            title (str): Title of the book.
            ISBN (str): ISBN identifier of the book.
            genre (str): Genre of the book.

        Returns:
            dict: New book document ready for insertion, or error message.
        """
        # ------------------ Google Books API ------------------
        try:
            google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}"
            google_books_response = requests.get(google_books_url).json()
            google_data = google_books_response["items"][0]["volumeInfo"]
        except Exception:
            return {"Error": f"No data returned from Google Books API for ISBN {ISBN}"}

        authors = " and ".join(google_data.get("authors", ["missing"]))
        publisher = google_data.get("publisher", "missing")
        published_date = google_data.get("publishedDate", "missing")

        # ------------------ OpenLibrary API ------------------
        try:
            openlib_url = f"https://openlibrary.org/search.json?q={ISBN}&fields=language"
            openlib_data = requests.get(openlib_url).json()
            language = openlib_data["docs"][0].get("language", ["missing"])
        except Exception:
            language = ["missing"]

        # ------------------ Gemini API ------------------
        try:
            genai.configure(api_key=genai_key)
            model = genai.GenerativeModel(model_name="gemini-2.0-flash")
            response = model.generate_content(
                f'Summarize the book "{title}" by {authors} in 5 sentences or less.'
            )
            summary = response.text or "missing"
        except Exception:
            summary = "missing"

        # ------------------ Final Book Document ------------------
        return {
            "id": str(ISBN),  # Assuming ISBN is the unique ID
            "title": title,
            "authors": authors,
            "ISBN": ISBN,
            "publisher": publisher,
            "publishedDate": published_date,
            "genre": genre,
            "language": language,
            "summary": summary
        }


    def addBook(self, title, ISBN, genre):
        """
        Creates a new book and inserts it into the MongoDB collection.

        Args:
            title (str): Book title.
            ISBN (str): Book ISBN (used as unique ID).
            genre (str): Book genre.

        Returns:
            str: ID of the created book or error message.
        """
        # Check for duplicate
        if self.books_col.find_one({"id": str(ISBN)}):
            return f"Book already exists with ISBN: {ISBN}"

        # Create enriched book document
        new_book = self.createNewBook(title, ISBN, genre)

        if "Error" in new_book:
            return new_book["Error"]

        # Insert into collection
        self.books_col.insert_one(new_book)

        return new_book["id"]

    def getBook(self, id):
        """
        Retrieves a Book from the collection by ID.

        Args:
            id (str or int): The ID of the book to retrieve.

        Returns:
            dict: The requested Book document.
        """
        book = self.books_col.find_one({"id": str(id)}, {"_id": 0})

        if book:
            return book
        else:
            return {"Error": f"No Book Exists with id: {id}"}

    def deleteBook(self, id):
        """
        Deletes a Book from the collection by ID.

        Args:
            id (str or int): The ID of the book to delete.

        Returns:
            dict: Success or error message.
        """
        result = self.books_col.delete_one({"id": str(id)})

        if result.deleted_count == 0:
            return {"Error": f"No Book Exists with id: {id}"}

        return {"Success": f"Book {id} deleted successfully"}

    def changeBook(self, book_data, book_id):
        """
        Updates fields of an existing book document in MongoDB.

        Args:
            book_data (dict): Dictionary of field names and new values.
            book_id (str or int): The ID of the book to update.

        Returns:
            dict: Success or error message.
        """

        # Check if book exists
        existing = self.books_col.find_one({"id": str(book_id)})
        if not existing:
            return {"Error": f"No Books Exists with id: {book_id}"}

        # (Optional) check for allowed fields
        allowed_fields = {
            "title",
            "authors",
            "publisher",
            "publishedDate",
            "genre",
            "language",
            "summary",
        }
        for field in book_data:
            if field not in allowed_fields:
                return {"Error": f"Field {field} is not a valid book field"}

        # Update the document in Mongo
        result = self.books_col.update_one({"id": str(book_id)}, {"$set": book_data})

        if result.modified_count == 0:
            return {"Error": "Update failed or no changes made"}

        return {"Success": f"Book {book_id} updated successfully."}

    def getBooksCollection(self, filters={}):
        """
        Retrieves all books that match given filter criteria.

        Args:
            filters (dict): Dictionary of field-value pairs to filter the books (e.g. {"genre": "fiction"}).

        Returns:
            list: A list of books (as plain dicts) matching the filter.
        """
        
        # convert string values if needed, MongoDB stores values as their real types
        query = {k: v for k, v in filters.items()}

        # execute the query
        books_cursor = self.books_col.find(query, {"_id": 0})  # exclude _id
    
        # convert cursor to list
        return list(books_cursor)
