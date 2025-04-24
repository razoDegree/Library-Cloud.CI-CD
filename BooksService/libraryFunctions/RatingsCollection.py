from libraryFunctions.Rating import Rating


class RatingsCollection:
    """
    A class to manage a collection of book ratings, allowing creation, update,
    deletion, and retrieval of rating data. Each rating is linked to a book ID.
    """

    def __init__(self):
        """
        Initializes an empty list of ratings.

        Attributes:
            ratings (list): A list of Rating objects.
        """
        self.ratings = []  # Holds the list of Rating Object

    def createRating(self, id, title):
        """
        Creates a new Rating object for a specific book.

        Args:
            id (str or int): The book's identifier.
            title (str): The title of the book.

        Returns:
            None
        """
        self.ratings.append(Rating(id, title))

    def addRatingValue(self, id, value):
        """
        Adds a numeric rating (1-5) to a specific book and updates the average.

        Args:
            id (str or int): The ID of the book to rate.
            value (int): The rating value (must be between 1 and 5).

        Returns:
            dict: Success or error message.
        """
        # Check if the value is int in range of 1 - 5
        if value not in [1, 2, 3, 4, 5]:
            return {"Error": "Value is not valid"}

        # Find the book
        rating_required = self.getRating(id)
        if not isinstance(rating_required, Rating):
            return rating_required

        # Update the values
        rating_required.values.append(value)

        # Calculate avg.
        prev_avg = rating_required.average
        values_len = len(rating_required.values)
        rating_required.average = round(
            sum(rating_required.values) / len(rating_required.values), 2
        )

        return {"Success": f"Book {id} avg. rating is {rating_required.average}"}

    def deleteRating(self, id):
        """
        Deletes the rating data for a specific book.

        Args:
            id (str or int): The ID of the book whose rating is to be deleted.

        Returns:
            dict: Success or error message.
        """
        # Find the book
        rating_required = self.getRating(id)
        if not isinstance(rating_required, Rating):
            return rating_required

        self.ratings.remove(rating_required)
        return {"Success": f"Book rating {id} deleted succesfully."}

    def getRatings(self):
        """
        Retrieves all ratings in the system in JSON format.

        Returns:
            list: A list of all book ratings as JSON.
        """
        requested_rates = []

        for book_rate in self.ratings:
            requested_rates.append(book_rate.toJson())

        return requested_rates

    def getRating(self, id):
        """
        Retrieves a specific book's rating object by ID.

        Args:
            id (str or int): The ID of the book.

        Returns:
            Rating: The corresponding Rating object.
            dict: Error message if not found.
        """
        # Find the book
        book_required = next((r for r in self.ratings if str(r.id) == str(id)), None)
        if not book_required:
            return {"Error": "Book does not exist"}
        return book_required

    def getTop3(self):
        """
        Retrieves the top 3 books with the highest average rating,
        where each has at least 3 ratings.

        Returns:
            list: A list of top 3 rated books in JSON format.
        """
        eligible = [r for r in self.ratings if len(r.values) >= 3]
        if not eligible:
            return []

        eligible.sort(key=lambda r: r.average, reverse=True)
        top3 = []
        cutoff = None

        for r in eligible:
            if len(top3) < 3:
                top3.append(r.toJsonTop3())
                cutoff = r.average
            elif r.average == cutoff:
                top3.append(r.toJsonTop3())
            else:
                break
        return top3
