from BooksCollection import BooksCollection

# ----------------> TESTING 
# CREATING BOOKS COLLECTION
bookCol = BooksCollection() 

# ADDING BOOKS
bookCol.addBook("Exodus", 9780553258479, "History")
bookCol.addBook("Harry Potter and the Philosopher's Stone", 9781408855652, "Fantasy")
bookCol.addBook("Hamlet", 9780743477123, "Fiction")

# GET BOOKS
print(bookCol.getBook(9781408855652))

# DELETE BOOKS
bookCol.deleteBook(9780553258479)

# PRINT LIST
bookCol.getBooksCollection()
