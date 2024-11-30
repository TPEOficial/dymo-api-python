class DymoAPIError(Exception):
    # Base class for exceptions in DymoAPI.
    def __init__(self, message):
        super().__init__(message)
        self.message = f"[Dymo API] {message}"

# Exception raised for errors in token validation.
class AuthenticationError(DymoAPIError): pass
# There are no tokens/uses available.
class RateLimitError(DymoAPIError): pass
# Invalid parameters.
class BadRequestError(DymoAPIError): pass
# Error on request.
class APIError(DymoAPIError): pass