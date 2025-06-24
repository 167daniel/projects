from pydantic import BaseModel, Field

""""
This module defines the data models used for validating incoming requests
and formatting API responses using Pydantic.

These models ensure type safety, enforce constraints (e.g., positive amounts),
and integrate with FastAPI’s automatic documentation.

Current Models:
- DepositRequest: Used to validate deposit operations
- WithdrawRequest: Used to validate withdrawal operations
- BalanceResponse: Defines the structure of balance retrieval responses

Note:
- All account numbers are represented as strings.
- Support for UUIDs and additional fields (e.g., currency) is reserved for future extensions.
"""


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to deposit; must be positive")


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to withdraw; must be positive")


class BalanceResponse(BaseModel):
    account_number: str  # Account number as a string; UUID support is planned as an extension
    balance: float
