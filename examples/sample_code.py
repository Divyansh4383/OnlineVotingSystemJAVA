"""
sample_code.py - A small, intentionally imperfect example for trying out
`python main.py review`, `bugs`, `improve`, and `docs` against a real file.
"""


def calculate_discount(price, discount_percent):
    # Bug: no validation, and float rounding not handled
    discount = price * discount_percent / 100
    return price - discount


def get_user(users, user_id):
    for u in users:
        if u["id"] == user_id:
            return u
    # Bug: implicitly returns None with no error handling for missing user


def process_orders(orders):
    total = 0
    for order in orders:
        total += order["amount"]  # Bug: KeyError if "amount" missing
    return total
