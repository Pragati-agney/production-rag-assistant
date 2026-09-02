class ProviderError(Exception):
    def __init__(
        self,
        message: str,
        retryable: bool,
    ):
        super().__init__(message)
        self.retryable = retryable


class DatabaseError(Exception):
    def __init__(
        self,
        message: str,
        retryable: bool,
    ):
        super().__init__(message)
        self.retryable = retryable
