class Rating:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.values = []  # Each number is between 1 to 5
        self.average = 0

    def toJson(self):
        return {
            "id": self.id,
            "title": self.title,
            "average": self.average,
            "values": self.values,
        }
        
    def toJsonTop3(self):
        return {
            "id": self.id,
            "title": self.title,
            "average": self.average
        }
