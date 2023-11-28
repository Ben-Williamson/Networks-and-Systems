class Message:
    def __init__(self, message, origin, type='message'):
        self.message = message
        self.origin = origin
        self.type = type

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def get_origin(self):
        return self.origin

    def get_message(self):
        return self.message

    def __str__(self):
        if self.type == 'forward':
            return str(self.message)
        return f'{self.origin}: [{self.type}] {self.message}'