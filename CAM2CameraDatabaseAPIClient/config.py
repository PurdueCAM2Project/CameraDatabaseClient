"""
This file is to keep track all constant variables used.
"""

SECRET_LENGTH = 71

"""
secret length is fixed as a 71 char long string in the current implementation.
It was previously 96 chars. We limit the length because our encryption algorithm.
does not take more chars.
"""

CLIENTID_LENGTH = 96

"""
we generate a fixed length ID for client in the API.
"""
