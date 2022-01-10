from fastapi import HTTPException


class UserHasAccountException(Exception):
    """User already has account."""


class InvalidEmailException(Exception):
    """Invalid email"""