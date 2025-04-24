class Loan:
    def __init__(self, memberName, ISBN, title, bookID, loanDate, loanID):
        self.memberName = memberName
        self.ISBN = ISBN
        self.title = title
        self.bookID = bookID
        self.loanDate = loanDate
        self.loanID = loanID
        
    def toJson(self):
        return {
            "memberName": self.memberName,
            "ISBN": self.ISBN,
            "title": self.title,
            "bookID": self.bookID,
            "loanDate": self.loanDate,
            "loanID": self.loanID,
        }
