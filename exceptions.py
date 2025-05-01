import traceback

class CustomError(Exception):
    """Exception raised for custom errors with detailed debug info."""

    def __init__(self, message, error_code):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

        stack = traceback.extract_stack()
        if len(stack) >= 2:
            last_frame = stack[-2]
            self.filename = last_frame.filename
            self.line_number = last_frame.lineno
        else:
            self.filename = "N/A"
            self.line_number = "N/A"

        self.exception_type = self.__class__.__name__

    def __str__(self):
        return (
            f"{self.exception_type}: {self.message} "
            f"(Error Code: {self.error_code})\n"
            f"File: {self.filename}, Line: {self.line_number}"
        )
