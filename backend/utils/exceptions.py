class GeminiAPIError(Exception):
    """Raised when the Gemini API request fails."""


class GeminiResponseError(Exception):
    """Raised when Gemini returns invalid or unusable data."""


class NotFoundError(Exception):
    """Raised when a database record does not exist."""
