from flask import Flask, request
from flask_restful import Resource, Api
from libraryFunctions.BooksCollection import BooksCollection
from libraryFunctions.RatingsCollection import RatingsCollection

app = Flask(__name__)
api = Api(app)

booksCol = BooksCollection()
ratingsCol = RatingsCollection()


class BookList(Resource):
    def get(self):
        return booksCol.getBooksCollection(request.args), 200

    def post(self):
        try:
            data = request.get_json()
        except:
            return {"Error": "Wrong data type (Unsupported media type)"}, 415

        # Check if the fields are valid in the request
        try:
            title = data["title"]
            ISBN = data["ISBN"]
            genre = data["genre"]
        except:
            return {"Error": "Unable to process the request"}, 422

        # Check if there is already book with the same ISBN
        if not isinstance(booksCol.getBook(ISBN), dict):
            return {"Error": f"Book already exists with ISBN: {ISBN}"}, 422

        # Add the book and Check if succeed
        new_book_id = booksCol.addBook(title, ISBN, genre)
        if str(new_book_id) != str(ISBN):
            return {"Error": str(new_book_id)}, 500

        # Create a /rating/{id} endpoint
        ratingsCol.createRating(new_book_id, title)

        return {"message": f"Book created successfully", "book_id": new_book_id}, 201


class Book(Resource):
    def get(self, id):
        requested_book = booksCol.getBook(id)
        if isinstance(requested_book, dict) and "Error" in requested_book:
            return requested_book, 404
        return requested_book.toJson(), 202

    def delete(self, id):
        result_books = booksCol.deleteBook(id)
        result_rating = ratingsCol.deleteRating(id)
        if "Success" in result_books and "Success" in result_rating:
            return result_books, 200
        return result_books, 404

    def put(self, id):
        try:
            data = request.get_json()
        except:
            return {"Error": "Wrong data type (Unsupported media type)"}, 415

        res = booksCol.changeBook(data, id)
        if "Error" in res:
            if "No Books Exists" in res["Error"]:
                return res, 404
            return res, 422

        return res, 200


class Ratings(Resource):
    def get(self):
        if request.args == {}:
            resulte = ratingsCol.getRatings()
            return resulte
        else:
            try:
                resulte = ratingsCol.getRating(request.args["id"])
            except:
                return {"Error": "Bad field value"}, 422
            if isinstance(resulte, dict):
                return resulte, 404
            return resulte.toJson(), 200


class Rating(Resource):
    def post(self, id):
        # Check if the file data type is JSON
        try:
            data = request.get_json()
        except:
            return {"Error": "Wrong data type (Unsupported media type)"}, 415

        # Check if the fields are valid in the request
        try:
            value = data["value"]
        except:
            return {"Error": "Unable to process the request"}, 422

        # Add the rating
        res = ratingsCol.addRatingValue(id, value)
        if "Error" in res:
            return res, 422
        else:
            return res, 201

    def get(self, id):
        resulte = ratingsCol.getRating(id)
        if isinstance(resulte, dict):
            return resulte, 404
        return resulte.toJson(), 200


class Top3(Resource):
    def get(self):
        return ratingsCol.getTop3()
    

api.add_resource(Top3, "/top")
api.add_resource(Rating, "/ratings/<string:id>")
api.add_resource(Ratings, "/ratings")
api.add_resource(BookList, "/books")
api.add_resource(Book, "/books/<string:id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
