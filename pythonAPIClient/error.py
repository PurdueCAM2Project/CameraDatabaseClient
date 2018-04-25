class Error(Exception):
    """
    Represent a generic error.
    """
    pass


class FormatError(Error):
    """
    Corresponends to 422 RequestFormatError in API.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

    pass


class ResourceNotFoundError(Error):
    """
    Corresponends to 404 ResourceNotFoundError in API.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

    pass


class AuthenticationError(Error):
    """
    Corresponends to 401 AuthenticationError in API.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

    pass


class InternalError(Error):
    """
    Corresponends to 500 InternalError in API.
    """

    def __init__(self):
        self.message = 'InternalError'

    def __str__(self):
        return str(self.message)

    pass


class ResourceConflictError(Error):
    """
    Corresponends to 409 ResourceConflictError in API.
    It is used in POST /cameras/create and PUT /cameras/{:camerID} route
    signaling 'legacyCameraIDAlreadyExist'
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

    pass


class AuthorizationError(Error):
    """
    Corresponends to 403 AuthorizationError in API.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

    pass


class InvalidClientIdError(Error):
    """
    Corresponends to 403 AuthorizationError in API.
    """

    def __init__(self):
        self.message = 'The Length of ClientID should be 96'

    def __str__(self):
        return str(self.message)

    pass


class InvalidClientSecretError(Error):
    """
    Corresponends to 403 AuthorizationError in API.
    """

    def __init__(self):
        self.message = 'The Length of ClientSecret should be 71'

    def __str__(self):
        return str(self.message)

    pass
