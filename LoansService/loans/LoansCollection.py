from pymongo import MongoClient
import requests
import uuid

# BOOKS_SERVICE_URL = "http://127.0.0.1:5001/books"
BOOKS_SERVICE_URL = "http://books:5000/books"


class LoansCollection:
    """
    Manages loan records for books, including creation, retrieval, and deletion.
    Integrates with an external Books service to fetch book metadata using ISBN.
    """

    def __init__(self):
        """
        Initializes the MongoDB connection and sets the loans collection.
        """
        uri = "mongodb://mongo:27017/"
        self.client = MongoClient(uri)
        self.database = self.client["library"]
        self.loans_col = self.database["loans"]

    def get_book_by_isbn(self, isbn):
        """
        Retrieves book details from the Books service using its ISBN.

        Args:
            isbn (str): The ISBN of the book to retrieve.

        Returns:
            dict: Book data if found, or an error message if not found or if request fails.
        """
        try:
            response = requests.get(f"{BOOKS_SERVICE_URL}?ISBN={isbn}")
            if response.status_code == 200:
                books = response.json()
                if books:
                    return books[0]
                else:
                    return {"Error": f"No Book Exists with ISBN: {isbn}"}
        except requests.RequestException:
            return {"Error": f"Couldnt get book {isbn}"}

    def createLoan(self, memberName, ISBN, loanDate):
        """
        Creates a loan record after validating:
        - Book exists in the Books service.
        - Book is not already loaned.
        - Member has fewer than 2 loans.

        Args:
            memberName (str): Name of the member requesting the loan.
            ISBN (str): ISBN of the book to be loaned.
            loanDate (str): Date of the loan in 'YYYY-MM-DD' format.

        Returns:
            dict: Loan document if successful, or error message if validation fails.
        """
        book = self.get_book_by_isbn(ISBN)
        if not book or "title" not in book or "id" not in book:
            return {"Error": f"No Book Exists with ISBN: {ISBN}, book: {book}"}

        # loanID - need to be genrate
        loanID = str(uuid.uuid4())

        # Check if book available
        count = 0
        if self.loans_col.find_one({"ISBN": ISBN}):
            return {"Error": f"Book with ISBN: {ISBN} already loaned."}

        count = len(list(self.loans_col.find({"memberName": memberName})))
        if count == 2:
            return {"Error": f"User have already 2 books"}

        # Create new instance of Loan
        newLoan = {
            "memberName": memberName,
            "ISBN": ISBN,
            "title": book["title"],
            "bookID": book["id"],
            "loanDate": loanDate,
            "loanID": loanID,
        }

        return newLoan

    def loanBook(self, memberName, ISBN, loanDate):
        """
        Validates and adds a loan to the database.

        Args:
            memberName (str): Name of the member.
            ISBN (str): ISBN of the book.
            loanDate (str): Date of the loan in 'YYYY-MM-DD' format.

        Returns:
            dict: Success message with loan ID, or error message if failed.
        """
        newLoan = self.createLoan(memberName, ISBN, loanDate)
        if "Error" in newLoan:
            return newLoan

        self.loans_col.insert_one(newLoan)
        # Change Book Status to unavailable
        return {"Success": f"Loan {newLoan['loanID']} approved"}

    def getLoanCollection(self, filters={}):
        """
        Retrieves loans that match the given filter criteria.

        Args:
            filters (dict): Dictionary of field-value pairs to filter loans (e.g., {"memberName": "Alice"}).

        Returns:
            list: List of matching loan records (excluding internal _id field).
        """
        # convert string values if needed, MongoDB stores values as their real types
        query = {k: int(v) if k == "ISBN" else str(v) for k, v in filters.items()}

        # execute the query
        loan_cursor = self.loans_col.find(query, {"_id": 0})  # exclude _id

        # convert cursor to list
        return list(loan_cursor)

    def returnLoan(self, loanID):
        """
        Deletes a loan record by its loan ID.

        Args:
            loanID (str): The ID of the loan to be deleted.

        Returns:
            dict: Success message or error if the loan ID does not exist.
        """
        if not self.loans_col.find_one({"loanID": str(loanID)}):
            return {"Error": f"No Loan Exists with id: {loanID}"}

        self.loans_col.delete_one({"loanID": str(loanID)})
        return {"Success": f"Loan {loanID} deleted successfully."}
