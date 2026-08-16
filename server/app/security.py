import os

import bcrypt


def _get_pepper():
    pepper = os.getenv("PASSWORD_PEPPER")
    if not pepper:
        raise RuntimeError(
            "PASSWORD_PEPPER could not be found in environment variables. "
            "Put the variable in the .env file before starting the server. "
        )
    return pepper.encode("utf-8")


def hash_password(password):
    pepper = _get_pepper()
    if not isinstance(password, str):
        raise TypeError("Password is not a string")

    password_bytes = password.encode("utf-8")

    combined = password_bytes + pepper
    salt = bcrypt.gensalt()  # Default 12-rounds
    password_hashed = bcrypt.hashpw(combined, salt)

    return password_hashed.decode("utf-8")


def verify_password(password, hashed):
    pepper = _get_pepper()
    if not isinstance(password, str):
        raise TypeError("Password is not a string")

    password_bytes = password.encode("utf-8")

    combined = password_bytes + pepper

    try:
        return bcrypt.checkpw(combined, hashed.encode("utf-8"))
    except ValueError:
        return False
