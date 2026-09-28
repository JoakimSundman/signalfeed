import getpass
import os
import secrets
import sys

from sqlalchemy import select

from app.database import session_creator
from app.models import User

MAX_ATTEMPTS = 3


def check_gate_password():
    correct = os.getenv("ADMIN_CLI_PASSWORD")
    if not correct:
        raise RuntimeError("ADMIN_CLI_PASSWORD is missing in environment variables.")

    for attempt in range(MAX_ATTEMPTS):
        entered = getpass.getpass("Admin CLI password: ")
        if secrets.compare_digest(entered, correct):
            return True
        print(f"Wrong password. Attempts left: {MAX_ATTEMPTS - attempt - 1}")

    print("Too many failed attempts, exiting...")
    sys.exit(1)


def prompt_username(session):
    while True:
        username = input("Enter a username: ")
        stmt = select(User).where(User.username == username)
        existing = session.execute(stmt).scalar_one_or_none()
        if not existing and username.strip() != "":
            return username
        print("Username already exists or is empty, pick another one")


def prompt_new_password():
    for attempt in range(MAX_ATTEMPTS):
        password = getpass.getpass("Password for the new user: ")
        repeated = getpass.getpass("Repeat the password for new user: ")
        if password == repeated and password.strip() != "":
            return password
        print(f"Password and repetition does not match. Attemps left: {MAX_ATTEMPTS - attempt - 1}")

    print("Too many failed attempts, exiting...")
    sys.exit(1)


def prompt_is_admin():
    is_admin = input("Is user an admin? [y/N] ").strip().lower()
    if is_admin == "y":
        return True
    else:
        return False


def create_user(session, username: str, password: str, is_admin: bool):
    """Hash, create user, commit"""
    pass


def main():
    session = session_creator()
    try:
        check_gate_password()
        username = prompt_username(session)
        password = prompt_new_password()
        is_admin = prompt_is_admin()
        create_user(session, username, password, is_admin)
        print(f"User '{username}' created.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
