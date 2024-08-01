class DymoAPIError(Exception):
    """Base class for exceptions in DymoAPI."""
    def __init__(self, message):
        super().__init__(message)
        self.message = f"[Dymo API] {message}"

class TokenValidationError(DymoAPIError):
    """Exception raised for errors in token validation."""
    pass