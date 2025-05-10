from flask import Flask, request
from flask_restful import Resource, Api
from loans.LoansCollection import LoansCollection

app = Flask(__name__)
api = Api(app)

loansCol = LoansCollection()


class LoanID(Resource):
    """
    RESTful resource for handling DELETE requests on /loans/<id>.

    Methods:
        delete(id): Deletes a loan by its loanID.
    """

    def delete(self, id):
        """
        Deletes the loan with the specified ID.

        Args:
            id (str): The loan ID to delete.

        Returns:
            Tuple: JSON response and HTTP status code.
                   - 200 if successful
                   - 404 if the loan ID does not exist
        """
        resulte = loansCol.returnLoan(id)
        if "Error" in resulte:
            return resulte, 404
        return resulte, 200


class Loan(Resource):
    """
    RESTful resource for handling POST and GET requests on /loans.

    Methods:
        post(): Creates a new loan based on the provided memberName, ISBN, and loanDate.
        get(): Returns a filtered list of current loans (if filters are given).
    """

    def post(self):
        """
        Handles loan creation.
        Validates JSON and required fields. Interacts with LoansCollection to add a loan.

        Expected JSON Format:
            {
                "memberName": <str>,
                "ISBN": <str>,
                "loanDate": <str in YYYY-MM-DD>
            }

        Returns:
            Tuple: JSON response and HTTP status code.
                   - 201 on success
                   - 415 if media type is wrong or if book already loaned/member has 2 loans
                   - 422 if fields are missing
        """
        try:
            data = request.get_json()
        except:
            return {"Error": "Wrong data type (Unsupported media type)"}, 415

        # Check if the fields are valid in the request
        try:
            memberName = data["memberName"]
            ISBN = data["ISBN"]
            loanDate = data["loanDate"]
        except:
            return {"Error": "Unable to process the request"}, 422

        result = loansCol.loanBook(memberName, ISBN, loanDate)
        if "Error" in result:
            return result, 415
        return result, 201

    def get(self):
        """
        Handles loan listing with optional filters.

        Example:
            GET /loans?memberName=Alice&ISBN=123456

        Returns:
            Tuple: List of loans and HTTP status code 200.
        """
        return loansCol.getLoanCollection(request.args), 200


api.add_resource(Loan, "/loans")
api.add_resource(LoanID, "/loans/<string:id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
