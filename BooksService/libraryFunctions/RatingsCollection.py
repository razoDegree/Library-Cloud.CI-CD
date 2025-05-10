from pymongo import MongoClient


class RatingsCollection:
    """
    Manages a MongoDB collection of book ratings.
    Provides functionality to create, update, delete, and retrieve rating data.
    Each rating is linked to a book by its ID.
    """

    def __init__(self):
        """
        Initializes the MongoDB connection and references the 'ratings' collection.
        """
        uri = "mongodb://mongo:27017/"
        self.client = MongoClient(uri)
        self.database = self.client["library"]
        self.ratings_col = self.database["ratings"]

    def createRating(self, id, title):
        """
        Creates a new rating entry for a book.

        Args:
            id (str or int): Book identifier.
            title (str): Title of the book.
        """
        new_rating = {
            "id": id,
            "title": title,
            "average": 0,
            "values": [],
        }

        self.ratings_col.insert_one(new_rating)

    def addRatingValue(self, id, value):
        """
        Adds a rating value (1–5) to a specific book and updates its average.

        Args:
            id (str or int): Book ID.
            value (int): Rating value (must be between 1 and 5).

        Returns:
            dict: Success or error message.
        """
        # Check if the value is int in range of 1 - 5
        if value not in [1, 2, 3, 4, 5]:
            return {"Error": "Value is not valid"}

        # Find the book
        if not self.ratings_col.find_one({"id": str(id)}):
            return []

        # Update the values
        result = self.ratings_col.update_one(
            {"id": str(id)}, {"$push": {"values": value}}
        )

        if result.modified_count == 0:
            return {"Error": "Update failed or no changes made"}

        # Calculate avg.
        rating_values = self.ratings_col.find_one({"id": str(id)})["values"]
        values_len = len(rating_values)

        average = round(sum(rating_values) / values_len, 2)
        result = self.ratings_col.update_one(
            {"id": str(id)}, {"$set": {"average": average}}
        )

        if result.modified_count == 0:
            return {"Error": "Update failed or no changes made"}

        return {"Success": f"Book {id} avg. rating is {average}"}

    def deleteRating(self, id):
        """
        Deletes the rating entry for a specific book.

        Args:
            id (str or int): Book ID.

        Returns:
            dict: Success or error message.
        """
        # Find the book
        if not self.ratings_col.find_one({"id": str(id)}):
            return []

        self.ratings_col.delete_one({"id": str(id)})
        return {"Success": f"Book rating {id} deleted succesfully."}

    def getRatings(self):
        """
        Retrieves all book ratings.

        Returns:
            list: List of all ratings (excluding MongoDB internal _id field).
        """
        return list(self.ratings_col.find({}, {"_id": 0}))

    def getRating(self, id):
        """
        Retrieves the rating details of a specific book.

        Args:
            id (str or int): Book ID.

        Returns:
            dict: Book rating data or error message.
        """
        # Find the book
        book_required = self.ratings_col.find_one({"id": id}, {"_id": 0})
        if not book_required:
            return {"Error": "Book does not exist"}
        return book_required

    def getTop3(self):
        """
        Retrieves the top 3 books with the highest average rating,
        only including books with at least 3 ratings.
        If there is a tie at the cutoff, includes all tied books.

        Returns:
            list: Top-rated books sorted by average rating.
        """
        pipeline = [
            {
                "$project": {
                    "id": 1,
                    "values": 1,
                    "average": { "$avg": "$values" },
                    "count": { "$size": "$values" }
                }
            },
            {
                "$match": { "count": { "$gte": 3 } }
            },
            {
                "$sort": { "average": -1 }
            }
        ]

        results = list(self.ratings_col.aggregate(pipeline))

        if not results:
            return []

        # Get top 3 and include ties
        top3 = []
        cutoff = None
        for r in results:
            if len(top3) < 3:
                top3.append({
                    "id": r["id"],
                    "average": r["average"],
                    "count": r["count"]
                })
                cutoff = r["average"]
            elif r["average"] == cutoff:
                top3.append({
                    "id": r["id"],
                    "average": r["average"],
                    "count": r["count"]
                })
            else:
                break

        return top3