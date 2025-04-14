from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException


class GenericException(JsonResponse):
    """
    Generic Exceptions will return status code of 500 and given error message
    """

    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 *args,
                 **kwargs):

        if message is None:
            self.message = "There is some internal issue, Please try again later."
        else:
            self.message = message

        self.code = code

        if data is None:
            self.response_data = []

        self.data = {
            "data": self.response_data,
            "status": {
                "code": self.code,
                "message": self.message
            }
        }

        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        super().__init__(*args, **kwargs, data=self.data)


class CustomBadRequest(GenericException):
    def __init__(self, message=None, data=None, code=400, *args, **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = 400

        if message is None:
            self.message = "Bad Request"

        self.status_code = 400


class CustomNotFound(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_404_NOT_FOUND,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_404_NOT_FOUND

        if message is None:
            self.message = "Not Found"

        self.status_code = status.HTTP_404_NOT_FOUND


class CustomAuthenticationFailed(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_401_UNAUTHORIZED,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_401_UNAUTHORIZED

        if message is None:
            self.message = "Not Found"

        self.status_code = status.HTTP_401_UNAUTHORIZED


class CustomPermissionDenied(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_403_FORBIDDEN,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_403_FORBIDDEN
        if message is None:
            self.message = "User is not allowed to perform this action"

        self.status_code = status.HTTP_403_FORBIDDEN


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 1400
    default_detail = 'Bad Request'
