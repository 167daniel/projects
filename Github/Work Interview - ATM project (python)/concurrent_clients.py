"""
concurrent_clients.py

Simulates two clients ("0" and "1") making concurrent requests to the Mini-ATM server.

Purpose:
- Test concurrency handling of the server.
- Verify correct API behavior with valid, invalid, and edge case inputs.
- Ensure no data races or inconsistent states occur under parallel load.
- Confirm proper handling of malformed or incomplete input.

Design:
- Uses Python's ThreadPoolExecutor to run two client test suites in parallel.
- Each client performs a sequence of operations:
  - Balance check
  - Valid deposit and withdrawal
  - Invalid deposits and withdrawals (e.g., zero, negative)
  - Overdraft test
  - Invalid route and method tests (only client "0")
  - Malformed JSON body test (only client "0")
  - Missing field test (only client "0")

Notes:
- The server must be running locally at http://localhost:8000 for the tests to succeed.
- The `requests` library is required.
- This script is designed for debugging and validation, not performance testing.
"""

import requests
import concurrent.futures

BASE_URL = "http://localhost:8000/accounts"

def print_result(response):
    """
    Helper to print HTTP response results.
    Prints success JSON or error detail.
    """
    if response.ok:
        print(f"Success: {response.json()}")
    else:
        try:
            detail = response.json().get('detail', 'No detail provided')
        except Exception:
            detail = 'No detail provided'
        print(f"Error {response.status_code}: {detail}")


def test_get_balance(account):
    """
    Test GET /accounts/{account}/balance endpoint.
    """
    resp = requests.get(f"{BASE_URL}/{account}/balance")
    print(f"[{account}] GET balance: ", end="")
    print_result(resp)


def test_deposit(account, amount):
    """
    Test POST /accounts/{account}/deposit with a given amount.
    """
    resp = requests.post(f"{BASE_URL}/{account}/deposit", json={"amount": amount})
    print(f"[{account}] POST deposit {amount}: ", end="")
    print_result(resp)


def test_withdraw(account, amount):
    """
    Test POST /accounts/{account}/withdraw with a given amount.
    """
    resp = requests.post(f"{BASE_URL}/{account}/withdraw", json={"amount": amount})
    print(f"[{account}] POST withdraw {amount}: ", end="")
    print_result(resp)


def test_invalid_route(account):
    """
    Test access to a non-existent route to verify 404 error.
    """
    resp = requests.get(f"{BASE_URL}/invalid_account/balance")
    print(f"[{account}] GET invalid route: ", end="")
    print_result(resp)


def test_wrong_method(account):
    """
    Test incorrect HTTP method usage (GET instead of POST).
    """
    resp = requests.get(f"{BASE_URL}/{account}/deposit")
    print(f"[{account}] GET on deposit endpoint (wrong method): Status {resp.status_code}")


def test_malformed_json(account):
    """
    Test sending syntactically incorrect JSON to the server.
    This should trigger a 422 or 400 validation error.
    """
    headers = {"Content-Type": "application/json"}
    bad_json = "{'amount': 100}"  # Invalid single quotes
    try:
        resp = requests.post(f"{BASE_URL}/{account}/deposit", data=bad_json, headers=headers)
        print(f"[{account}] POST malformed JSON: Status {resp.status_code} | Response: {resp.text}")
    except Exception as e:
        print(f"[{account}] POST malformed JSON: Exception occurred: {e}")


def test_missing_field(account):
    """
    Test sending a request with a missing 'amount' field in the body.
    Should raise 422 validation error from FastAPI.
    """
    resp = requests.post(f"{BASE_URL}/{account}/deposit", json={})
    print(f"[{account}] POST missing field: ", end="")
    print_result(resp)


def run_tests_for_account(account):
    """
    Runs a battery of tests simulating normal and edge use cases for a single account.

    Includes:
    - Valid and invalid deposits/withdrawals
    - Overdraft behavior
    - Invalid endpoint usage
    - JSON validation edge cases
    """
    print(f"\n==== Starting tests for account {account} ====")

    test_get_balance(account)

    # Deposit tests
    test_deposit(account, 500)    # valid
    test_deposit(account, 0)      # zero amount (invalid)
    test_deposit(account, -100)   # negative amount (invalid)

    # Withdraw tests
    test_withdraw(account, 200)   # valid
    test_withdraw(account, 0)     # zero amount (invalid)
    test_withdraw(account, -50)   # negative amount (invalid)
    test_withdraw(account, 2000)  # overdraft allowed (should succeed)

    test_get_balance(account)

    if account == "0":
        # Extra edge case tests (only client "0")
        resp = requests.post(f"{BASE_URL}/9999/withdraw", json={"amount": 50})
        print(f"[9999] POST withdraw 50: ", end="")
        print_result(resp)

        test_invalid_route(account)
        test_wrong_method(account)
        test_malformed_json(account)
        test_missing_field(account)

    print(f"==== Finished tests for account {account} ====\n")


if __name__ == "__main__":
    # Run both client test suites in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run_tests_for_account, acc) for acc in ["0", "1"]]
        concurrent.futures.wait(futures)
