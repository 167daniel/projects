from utils import InvalidAmount


# from utils import InsufficientFunds  # For future extension if there is overdraft limit.


class Account:
    """
    Represents a single bank account.

    Attributes:
        account_number (str): The unique identifier for the account.
        balance (float): Current balance of the account (default: 0).
        currency (str): Currency type (default: "USD").
    """

    def __init__(self, account_number: str, balance: float = 0.0, currency: str = "USD",
                 overdraft_limit: float = float("inf")):
        """
        Initialize a new account.

        Args:
            account_number (str): Unique ID for the account.
            balance (float): Initial balance (default: 0.0).
            currency (str): Currency type (default: "USD"), Extension placeholder, not enforced yet.
            overdraft_limit (float): How far below zero the account can go (default: unlimited).

        """
        self.account_number = account_number
        self.balance = balance
        self.overdraft_limit = overdraft_limit

        # Placeholder for future extension:
        # self.transaction_history = []
        # self.currency = currency

    def deposit(self, amount: float) -> float:
        """
        Deposit a positive amount to the account.

        Args:
            amount (float): The amount to deposit.

        Returns:
            float: The new balance.

        Raises:
            InvalidAmount: If the amount is not positive.
        """
        if amount <= 0:
            raise InvalidAmount(f"Deposit amount must be positive, got {amount}")
        self.balance += amount
        # Future: Add transaction record here
        return self.balance

    def withdraw(self, amount: float) -> float:
        """
        Withdraw a positive amount from the account.

        Args:
            amount (float): The amount to withdraw.

        Returns:
            float: The new balance.

        Raises:
            InvalidAmount: If the amount is not positive.
            InsufficientFunds: (future) If withdrawal exceeds overdraft limit.
        """
        if amount <= 0:
            raise InvalidAmount(f"Withdrawal amount must be positive, got {amount}")
        # Overdraft is allowed for now; enforce later if needed
        self.balance -= amount
        # Future: Add transaction record here
        return self.balance

    def get_balance(self) -> float:
        """
        Retrieve the current account balance.

        Returns:
            float: The current balance.
        """
        return self.balance
