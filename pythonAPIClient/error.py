class Error(Exception):
    """
    Represent a generic error.
    """
    pass


class FormatError(Error):
    """
    Corresponends to 422 RequestFormatError in API.
    """
    pass

class ResourceNotFoundError(Error):
    """
    Corresponends to 404 ResourceNotFoundError in API.
    """
    pass

class AuthenticationError(Error):
    """
    Corresponends to 401 AuthenticationError in API.
    """
    pass

class InternalError(Error):
    """
    Corresponends to 500 InternalError in API.
    """
    pass

class ResourceConflictError(Error):
    """
    Corresponends to 409 ResourceConflictError in API.
    It is only used in /cams/create route
    signaling 'cameraIDAlreadyExist'
    """
    pass

class AuthorizationError(Error):
    """
    Corresponends to 403 AuthorizationError in API.
    """
    pass