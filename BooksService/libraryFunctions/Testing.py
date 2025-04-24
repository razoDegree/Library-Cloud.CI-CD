# from BooksCollection import BooksCollection
from RatingsCollection import RatingsCollection

# ----------------> TESTING
# CREAT COLLECTION
# bookCol = BooksCollection()
ratesCol = RatingsCollection()

# ADDING BOOKS
ratesCol.createRating(1, "Exodus")
ratesCol.createRating(2, "Harry Potter and the Philosopher's Stone")
ratesCol.createRating(3, "Hamlet")
ratesCol.createRating(4, "Exodus")
ratesCol.createRating(5, "Harry Potter and the Philosopher's Stone")
ratesCol.createRating(6, "Hamlet")
ratesCol.createRating(7, "Hamlet")

# ADDING RATING VALUES
ratesCol.addRatingValue(1, 2)
ratesCol.addRatingValue(1, 2)
ratesCol.addRatingValue(1, 2)

ratesCol.addRatingValue(2, 3)
ratesCol.addRatingValue(2, 3)
ratesCol.addRatingValue(2, 3)
ratesCol.addRatingValue(2, 3)

ratesCol.addRatingValue(3, 5)
ratesCol.addRatingValue(3, 5)
ratesCol.addRatingValue(3, 5)

ratesCol.addRatingValue(4, 4)
ratesCol.addRatingValue(4, 4)
ratesCol.addRatingValue(4, 4)

ratesCol.addRatingValue(5, 5)

ratesCol.addRatingValue(6, 4)
ratesCol.addRatingValue(6, 4)
ratesCol.addRatingValue(6, 4)

ratesCol.addRatingValue(7, 4)
ratesCol.addRatingValue(7, 4)
ratesCol.addRatingValue(7, 4)

# DELETE RATING
# ratesCol.deleteRating(1)

# PRINT LIST
# print(ratesCol.getRatings())
# print("\n")
print(ratesCol.getTop3())
