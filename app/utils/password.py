import re

def validate_password_complexity(password: str) -> None:

    if not re.search(r'[A-Za-z]', password):
        raise ValueError('Password must contain at least one letter.')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit.')
