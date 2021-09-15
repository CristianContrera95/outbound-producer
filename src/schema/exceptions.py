class InvalidData(Exception):
    def __init__(self, message, data=None, ):
        self.message = message
        self.data = data
        super().__init__(self.message)

    def __str__(self):
        return self.message