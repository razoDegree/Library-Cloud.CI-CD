from libraryFunctions.Rating import Rating


class RatingsCollection:
    def __init__(self):
        self.ratings = []  # Holds the list of Rating Object
        # self.top3 = [] # Holds the indexs of the top 3 books
        # self.top3_min = 0 # Holds the minimal value in order to get into top 3

    # POST /books create /ratings/{id} endpoint VVV
    def createRating(self, id, title):
        self.ratings.append(Rating(id, title))

    # POST /ratings/{id}/values 
    def addRatingValue(self, id, value):
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
        rating_required.average = (prev_avg * (values_len - 1) + value) / values_len

        return {"Success": f"Book {id} avg. rating is {rating_required.average}"}

    # DELETE /books/{id} delete automate /ratings/{id} VVV
    def deleteRating(self, id):
        # Find the book
        rating_required = self.getRating(id)
        if not isinstance(rating_required, Rating):
            return rating_required
        
        self.ratings.remove(rating_required)
        return {"Success": f"Book rating {id} deleted succesfully."}
        
    # GET /ratings VVV
    def getRatings(self):
        requested_rates = []

        for book_rate in self.ratings:
            requested_rates.append(book_rate.toJson())

        return requested_rates

    # GET /ratings?id=<string> and VVV
    # GET /ratings/{id} 
    def getRating(self, id):
        # Find the book
        book_required = None

        for book_rating in self.ratings:
            if str(book_rating.id) == str(id):
                book_required = book_rating
        if book_required is None:
            return {"Error": "Book isn't exsists"}

        return book_required
 
    # GET /top 
    def getTop3(self):
        self.ratings = sorted(self.ratings, key=lambda rate: rate.average, reverse=True)

        top3 = []
        min_avg_top3 = 0

        for book_rating in self.ratings:
            if len(book_rating.values) > 2 and min_avg_top3 <= book_rating.average:
                top3.append(book_rating.toJsonTop3())
                if len(top3) == 3:
                    min_avg_top3 = book_rating.average
            elif len(book_rating.values) > 2:
                break

        return top3
