from typing import Dict
from account import Account
from utils import AccountNotFound

"""
This module manages the in-memory storage of account objects for the Mini ATM system.

Responsibilities:
- Maintain a dictionary mapping account numbers to Account instances.
- Provide functions to retrieve, create, and in further versions delete accounts.
- Initialize example accounts for testing purposes.
- Raise appropriate exceptions if accounts are not found or duplicates are created.

Note:
- Data is stored only in-memory and will be lost if the server restarts.
- Account creation and deletion are currently out of scope and mainly included for testing and future extension.
"""

# In-memory dictionary holding all accounts
# Keys are account numbers (strings) which uniquely identify each account.
# Values are Account instances storing the account’s state (balance, etc.).
# This design allows O(1) lookup of accounts by their account number
# Important: The dictionary keys MUST match the 'account_number' attribute of the corresponding Account object for
# consistency and correctness.
accounts: Dict[str, Account] = {}


def get(account_number: str) -> Account:
    """Retrieve an account by its account number.

    Raises:
        AccountNotFound: If the account does not exist.
    """
    if account_number not in accounts:
        raise AccountNotFound(f"Account '{account_number}' not found.")
    return accounts[account_number]


def create(account_number: str, initial_balance: float = 0.0) -> Account:
    """Create a new account with an initial balance.

    Raises:
        ValueError: If account already exists.

    Note:
        Account creation is currently out of scope but provided for testing and future extension.
    """
    if account_number in accounts:
        raise ValueError(f"Account '{account_number}' already exists.")
    account = Account(account_number=account_number, balance=initial_balance)
    accounts[account_number] = account
    return account


def initialize_accounts():
    """Initialize the in-memory store with two example accounts for testing.

    Note:
        This function is for testing convenience and not part of the assignment requirements.
    """
    accounts.clear()
    accounts["0"] = Account(account_number="0", balance=1000.0)
    accounts["1"] = Account(account_number="1", balance=1000.0)

# === Future Extension (placeholders) ===
# def delete(account_number: str):
#    """Delete an account (planned extension).
#
#    To be implemented if account deletion is required in the future.
#    """
#    pass
