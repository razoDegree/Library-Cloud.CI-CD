from libraryFunctions.Private import genai_key
import requests
import google.generativeai as genai  # Gemini API Library
from pymongo import MongoClient



class BooksCollection:
    """
    Manages a MongoDB collection of books, allowing creation, retrieval,
    updating, deletion, and filtering using metadata enrichment from external APIs.
    """

    def __init__(self):
        """
        Initializes a MongoDB connection and sets a reference to the 'books' collection.
        """

        uri = "mongodb://mongo:27017/"
        self.client = MongoClient(uri)
        self.database = self.client["library"]
        self.books_col = self.database["books"]

    def createNewBook(self, title, ISBN, genre):
        """
        Constructs a new book document enriched with metadata from Google Books,
        OpenLibrary, and Gemini APIs.

        Args:
            title (str): Title of the book.
            ISBN (str): ISBN of the book (used as a unique identifier).
            genre (str): Genre of the book.

        Returns:
            dict: A complete book document or an error message.
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
        Creates and inserts a new book into the collection if it doesn't already exist.

        Args:
            title (str): Book title.
            ISBN (str): Book ISBN.
            genre (str): Book genre.

        Returns:
            str: The book ID or an error message.
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
        Retrieves a book by its ID.

        Args:
            id (str or int): Book ID.

        Returns:
            dict: Book document or an error message.
        """
        book = self.books_col.find_one({"id": str(id)}, {"_id": 0})

        if book:
            return book
        else:
            return {"Error": f"No Book Exists with id: {id}"}

    def deleteBook(self, id):
        """
        Deletes a book by its ID.

        Args:
            id (str or int): Book ID.

        Returns:
            dict: Success or error message.
        """
        result = self.books_col.delete_one({"id": str(id)})

        if result.deleted_count == 0:
            return {"Error": f"No Book Exists with id: {id}"}

        return {"Success": f"Book {id} deleted successfully"}

    def changeBook(self, book_data, book_id):
        """
        Updates fields of an existing book document.

        Args:
            book_data (dict): Fields to update (e.g., {"genre": "fiction"}).
            book_id (str or int): Book ID.

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
        Retrieves books that match the specified filters.

        Args:
            filters (dict): Filter criteria (e.g., {"genre": "fiction"}).

        Returns:
            list: List of matching books (excluding the _id field).
        """
        
        # convert string values if needed, MongoDB stores values as their real types
        query = {k: int(v) if k == 'ISBN' else str(v) for k, v in filters.items()}

        # execute the query
        books_cursor = self.books_col.find(query, {"_id": 0})  # exclude _id
    
        # convert cursor to list
        return list(books_cursor)
