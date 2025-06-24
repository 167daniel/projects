# === Core Exceptions ===
class AccountNotFound(Exception):
    """Raised when an account is not found."""
    pass


class InvalidAmount(Exception):
    """Raised when an amount is invalid (<= 0)."""
    pass


class InsufficientFunds(Exception):
    """Raised when withdrawal amount exceeds balance (if overdraft not allowed)."""
    pass

# === Future Extension Exceptions (placeholders) ===
#
# class AccountAlreadyExists(Exception):
#    """Raised when attempting to create an account that already exists."""
#    pass

# class OverdraftLimitExceeded(Exception):
#     """Raised when withdrawal exceeds overdraft limit."""
#     pass

# class AuthenticationError(Exception):
#     """Raised when user authentication fails."""
#     pass
