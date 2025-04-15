from flask import Flask, request
from flask_restful import Resource, Api
from libraryFunctions.BooksCollection import BooksCollection

app = Flask(__name__)
api = Api(app)

booksCol = BooksCollection()


class BookList(Resource):
    def get(self):
        return booksCol.getBooksCollection(request.args), 200

    def post(self):
        # Check if the file data type is JSON
        try:
            data = request.get_json()
        except:
            return {"error": "Wrong data type (Unsupported media type)"}, 415

        # Check if the fields are valid in the request
        try:
            title = data["title"]
            ISBN = data["ISBN"]
            genre = data["genre"]
        except:
            return {"error": "Unable to process the request"}, 422

        # Check if there is already book with the same ISBN
        if not isinstance(booksCol.getBook(ISBN), dict):
            return {"error": f"Book already exists with ISBN: {ISBN}"}, 422

        # Add the book and Check if succeed
        new_book_id = booksCol.addBook(title, ISBN, genre)
        if str(new_book_id) != str(ISBN):
            return {"error": str(new_book_id)}, 500

        return {"message": f"Book created successfully", "book_id": new_book_id}, 201

    
class Book(Resource):
    def get(self, id):
        requested_book = booksCol.getBook(id)
        if isinstance(requested_book, dict) and "Error" in requested_book:
            return requested_book, 404
        return requested_book.toJson(), 202

    def delete(self, id):
        result = booksCol.deleteBook(id)
        if "Success" in result:
            return result, 200
        return result, 404

    def put(self, id):
        try:
            data = request.get_json()
        except:
            return {"error": "Wrong data type (Unsupported media type)"}, 415
        
        res = booksCol.changeBook(data, id)
        if "Error" in res:
            if "No Books Exists" in res["Error"]:
                return res, 404
            return res, 422
        
        return res, 200

api.add_resource(BookList, "/books")
api.add_resource(Book, "/books/<string:id>")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
