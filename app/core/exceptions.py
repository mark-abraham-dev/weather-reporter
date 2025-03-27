from fastapi import HTTPException, status


class WeatherAPIException(Exception):
    """Exception raised for errors in the weather API requests"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(Exception):
    """Exception raised for database errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(HTTPException):
    """Exception for resource not found errors"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    """Exception for bad request errors"""

    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
