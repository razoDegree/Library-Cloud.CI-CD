from loans.Loan import Loan
import requests
import uuid


BOOKS_SERVICE_URL = "http://127.0.0.1:5001/books"
# BOOKS_SERVICE_URL = "http://books-service:5001/books"


class LoansCollection:
    """
    This class manages loan records for books, including creation,
    retrieval, and deletion. It integrates with an external Books service
    to fetch book information based on ISBN.

    Attributes:
        loans (list): In-memory storage of Loan objects.
    """

    def __init__(self):
        self.loans = []

    def get_book_by_isbn(self, isbn):
        """
        Retrieve a book's details from the Books service using its ISBN.

        Args:
            isbn (str): The ISBN of the book to look up.

        Returns:
            dict: Book data if found, or an error message if not found or if the request fails.
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
        Create a loan record after validating:
        - Book exists in the Books service.
        - Book is not already loaned.
        - Member has fewer than 2 loans.

        Args:
            memberName (str): Name of the member requesting the loan.
            ISBN (str): ISBN of the book.
            loanDate (str): Date of loan in 'YYYY-MM-DD' format.

        Returns:
            Loan: A new Loan object if successful.
            dict: Error message if validations fail.
        """
        book = self.get_book_by_isbn(ISBN)
        try:
            title = book["title"]
            bookID = book["id"]
        except:
            return {"Error": f"No Book Exists with ISBN: {ISBN}"}

        # loanID - need to be genrate
        loanID = uuid.uuid4()

        # Check if book available
        count = 0
        for loan in self.loans:
            if loan.ISBN == ISBN:
                return {"Error": f"Book with ISBN: {ISBN} already loaned."}
            if loan.memberName == memberName:
                count += 1
                if count == 2:
                    return {"Error": f"User have already 2 books"}

        # Create new instance of Loan
        newLoan = Loan(memberName, ISBN, title, bookID, loanDate, loanID)

        return newLoan

    def loanBook(self, memberName, ISBN, loanDate):
        """
        Handle the POST /loans request.
        Validates the loan and adds it to the loan list if successful.

        Args:
            memberName (str): Name of the member.
            ISBN (str): ISBN of the book.
            loanDate (str): Date of the loan.

        Returns:
            dict: Success message with loanID or error message.
        """
        newLoan = self.createLoan(memberName, ISBN, loanDate)
        if not isinstance(newLoan, Loan):
            return newLoan

        self.loans.append(newLoan)
        # Change Book Status to unavailable
        return {"Success": f"Loan {newLoan.loanID} approved"}

    def getLoanCollection(self, filters={}):
        """
        Handle GET /loans and GET /loans?field=value...
        Retrieves all loans matching the given filters.

        Args:
            filters (dict): Key-value pairs to filter loans by their attributes.

        Returns:
            list: A list of JSON-serializable loan dicts matching the filters.
        """
        requested_loans = []

        for loan in self.loans:
            match = True
            for field, value in filters.items():
                if not hasattr(loan, field):
                    match = False
                    break

                field_value = getattr(loan, field)

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
                requested_loans.append(loan.toJson())

        return requested_loans

    def returnLoan(self, loanID):
        """
        Handle DELETE /loans/{loanID}.
        Deletes a loan from the list by its ID.

        Args:
            loanID (str): The ID of the loan to delete.

        Returns:
            dict: Success message or error if the loan ID does not exist.
        """
        try:
            loan_to_delete = next(
                (loan for loan in self.loans if loan.loanID == str(loanID)), None
            )
            self.loans.remove(loan_to_delete)  # Remove it from the list

        except:
            return {"Error": f"No Loan Exists with id: {loanID}"}

        return {"Success": f"Loan {loanID} deleted successfully."}
