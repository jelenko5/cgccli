import json


class BadAPIResponse(Exception):
    DEFAULT_MESSAGE = 'Something went wrong during communication with API. More info: \n'

    def __init__(self, message, error_code=None):
        self.msg = self.DEFAULT_MESSAGE + json.dumps(message, indent=4)
        self.error_code = error_code

    def __str__(self):
        return self.msg

