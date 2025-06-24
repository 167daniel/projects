"""
api.py

This module defines the FastAPI route handlers for the Mini-ATM system.

Responsibilities:
- Map HTTP requests to internal logic
- Validate incoming request data using Pydantic models
- Invoke business logic from the Account class and storage module
- Handle and translate known exceptions into proper HTTP responses
- Log key events for debugging and monitoring

Endpoints:
- GET    /accounts/{account_number}/balance    → Retrieve current balance
- POST   /accounts/{account_number}/deposit    → Deposit funds
- POST   /accounts/{account_number}/withdraw   → Withdraw funds

Note:
- Error handling is part of the core system, even though not demanded - since seems necessary
- Logging is minimal and intended for basic tracing/debugging
"""

from fastapi import APIRouter, HTTPException
from models import DepositRequest, WithdrawRequest, BalanceResponse
from storage import get
from utils import AccountNotFound, InvalidAmount
import logging

# Create API router instance to be included in the main app
router = APIRouter()

# Configure basic logging (logs to stdout)
logger = logging.getLogger("atm_api")
logging.basicConfig(level=logging.INFO)


@router.get("/accounts/{account_number}/balance", response_model=BalanceResponse)
def get_balance(account_number: str):
    """
    Retrieve the balance of the specified account.

    Returns:
        BalanceResponse containing the current balance.
    Raises:
        404 if the account is not found.
    """
    try:
        account = get(account_number)
        logger.info(f"Retrieved balance for account {account_number}")
        return BalanceResponse(account_number=account.account_number, balance=account.balance)
    except AccountNotFound:
        logger.warning(f"Balance request failed: Account {account_number} not found")
        raise HTTPException(status_code=404, detail="Account not found")


@router.post("/accounts/{account_number}/deposit", response_model=BalanceResponse)
def deposit(account_number: str, request: DepositRequest):
    """
    Deposit a positive amount into the specified account.

    Request Body:
        DepositRequest with amount > 0

    Returns:
        BalanceResponse with updated balance.
    Raises:
        404 if account does not exist.
        400 if the amount is invalid (non-positive).
    """
    try:
        account = get(account_number)
        account.deposit(request.amount)
        logger.info(f"Deposited {request.amount} to account {account_number}")
        return BalanceResponse(account_number=account.account_number, balance=account.balance)
    except AccountNotFound:
        logger.warning(f"Deposit failed: Account {account_number} not found")
        raise HTTPException(status_code=404, detail="Account not found")
    except InvalidAmount:
        logger.warning(f"Deposit failed: Invalid amount for account {account_number}")
        raise HTTPException(status_code=400, detail="Invalid amount")


@router.post("/accounts/{account_number}/withdraw", response_model=BalanceResponse)
def withdraw(account_number: str, request: WithdrawRequest):
    """
    Withdraw a positive amount from the specified account.

    Request Body:
        WithdrawRequest with amount > 0

    Returns:
        BalanceResponse with updated balance.
    Raises:
        404 if account does not exist.
        400 if the amount is invalid (non-positive or exceeds overdraft limit).
    """
    try:
        account = get(account_number)
        account.withdraw(request.amount)
        logger.info(f"Withdrew {request.amount} from account {account_number}")
        return BalanceResponse(account_number=account.account_number, balance=account.balance)
    except AccountNotFound:
        logger.warning(f"Withdrawal failed: Account {account_number} not found")
        raise HTTPException(status_code=404, detail="Account not found")
    except InvalidAmount:
        logger.warning(f"Withdrawal failed: Invalid amount for account {account_number}")
        raise HTTPException(status_code=400, detail="Invalid amount")
