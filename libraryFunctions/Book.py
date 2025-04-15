import json


class Book:
    def __init__(
        self,
        title,
        authors,
        ISBN,
        publisher,
        publishedDate,
        genre,
        language,
        summary,
        id,
        rating=[],
    ):
        self.title = title
        self.authors = authors
        self.ISBN = ISBN
        self.publisher = publisher
        self.publishedDate = publishedDate
        self.genre = genre
        self.language = language
        self.summary = summary
        self.id = id
        self.rating = rating
        self.ratingAvg = 0

    # Returns the book as JSON object
    def toJson(self):
        # return json.dumps(self.__dict__)
        return {
            "title": self.title,
            "authors": self.authors,
            "ISBN": self.ISBN,
            "publisher": self.publisher,
            "publishedDate": self.publishedDate,
            "genre": self.genre,
            "language": self.language,
            "summary": self.summary,
            "id": self.id,
            "rating": self.rating,
            "ratingAvg": self.ratingAvg,
        }

    def toString(self):
        return f"[{self.id}] Title: {self.title}, ISBN: {self.ISBN}, Authors: {self.authors}, Published Date: {self.publishedDate}, Lang: {self.language}, Summary: {self.summary}"
