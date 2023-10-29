import random
import string
import time
from typing import *
from dataclasses import dataclass
import hashlib
import base64

from ext.database_manager import DatabaseManager

max_username_length = 20
min_username_length = 4

max_password_length = 20
min_password_length = 8

allowed_chars = string.ascii_letters + string.digits + '_!@#'


class Hasher:
    def __init__(self, algorithm: str = 'sha512') -> None:
        self.algorithm = algorithm

    def hash(self, s: str) -> str:
        return hashlib.new(self.algorithm, s.encode()).hexdigest()

    @staticmethod
    def equal_hashes(h1: str, h2: str) -> bool:
        return h1 == h2

    @staticmethod
    def generate_salt(salt_length: int = 32) -> str:
        """
        Generate a salt
        :param salt_length: Length of the salt
        :return: Salt as string
        """
        return ''.join(random.choice(allowed_chars) for _ in range(salt_length))


class InvalidArgumentException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


@dataclass
class CheckedParameter:
    valid: bool
    message: str
    parameter: str = ''


class StringUtils:

    @staticmethod
    def __matches_length(s: str, min_length: int, max_length: int) -> bool:
        """
        Check if a string matches a length
        :param s: String to check
        :param min_length: Minimum length of the string
        :param max_length: Maximum length of the string
        :return: True if matches, False otherwise
        """
        # length must be between min_length and max_length or equal to one of them
        if StringUtils.is_empty(s):
            return True
        return not (min_length <= len(s) <= max_length)

    @staticmethod
    def is_empty(s: str) -> bool:
        """
        Check if a string is empty
        :param s: String to check
        :return: True if empty, False otherwise
        """
        if s is None:
            return True
        return len(s.strip()) == 0

    @staticmethod
    def __only_valid_chars(s: str, valid_chars: str) -> bool:
        """
        Check if a string only contains valid characters
        :param s: String to check
        :param valid_chars: Valid characters
        :return: True if only contains valid characters, False otherwise
        """
        for char in s:
            if char not in valid_chars:
                return False
        return True

    @staticmethod
    def validate_username(username: str) -> CheckedParameter:
        """
        Check if a username is valid
        :param username: Username as string (plain text)
        :return: True if valid, False otherwise
        """
        result: CheckedParameter = CheckedParameter(valid=False,
                                                    message='',
                                                    parameter=username)

        if StringUtils.__matches_length(username, min_username_length, max_username_length):
            result.message = f'Username length must be between {min_username_length} and {max_username_length}'
            return result

        if not StringUtils.__only_valid_chars(username, allowed_chars):
            result.message = 'Username must only contain letters and digits'
            return result

        result.valid = True
        return result

    @staticmethod
    def hash_password(password: str, hasher: Hasher) -> str:
        """
        Hash a password with sha256
        :param password: Password as string (base64 encoded)
        :param hasher: Hasher instance to hash the password
        :return: Hashed password
        """
        return hasher.hash(password)

    @staticmethod
    def add_salt_to_hashed_password(password: str, hasher: Hasher, salt: str) -> str:
        """
        Add salt to a hashed password
        :param password: Sha256 hashed password
        :param hasher: Hasher instance to hash the password
        :param salt: Salt to add to the hashed password
        :return: Salted password
        """
        return hasher.hash(password + salt)

    @staticmethod
    def validate_password(password: str, hasher: Hasher, salt: str) -> CheckedParameter:
        """
        Check if a password is valid
        :param password: Password as string (base64 encoded)
        :param hasher: Hasher instance to hash the password
        :param salt: Salt to add to the hashed password
        :return: True if valid, False otherwise
        """
        # make password to plain text
        password = base64.b64decode(password).decode()
        hashed_password: str = StringUtils.hash_password(password, hasher)
        hashed_salted_password: str = StringUtils.add_salt_to_hashed_password(hashed_password, hasher, salt)

        result: CheckedParameter = CheckedParameter(valid=False,
                                                    message='',
                                                    parameter=hashed_salted_password)

        if StringUtils.__matches_length(password, min_password_length, max_password_length):
            print(password)
            result.message = f'Password length must be between {min_password_length} and {max_password_length}'
            return result

        if not StringUtils.__only_valid_chars(password, allowed_chars):
            result.message = 'Password must only contain letters and digits'
            return result

        del password  # make sure password is deleted from memory

        result.valid = True
        return result

    @staticmethod
    def generate_token(length: int, token_chars: str) -> str:
        """
        Generate a random token
        :param length: Length of the token
        :param token_chars: Characters to use for the token
        :return: Random token
        """
        return ''.join(random.choice(token_chars) for _ in range(length))

    # generate timestamp for when the token expires
    @staticmethod
    def generate_expiration_time(duration: int) -> str:
        """
        Generate a timestamp for when the token expires
        :return: Timestamp
        """
        return str(int(time.time()) + duration)

    @staticmethod
    def is_after_expiration_time(expires_at: str) -> bool:
        """
        Check if a token is expired
        :param expires_at: Timestamp when the token expires
        :return: True if expired, False otherwise
        """
        return int(time.time()) > int(expires_at)


class LoginUtils:
    def __init__(self, db: DatabaseManager, hasher: Hasher) -> None:
        self.__db: DatabaseManager = db
        self.__hasher: Hasher = hasher

    def username_exists(self, username: str) -> bool:
        """
        Check if a username exists
        :param username: Username to check in plain text
        :return: True if exists, False otherwise
        """
        return self.__db.username_exists(username)

    def get_user_id(self, username: str) -> int:
        """
        Get a user ID
        :param username: Username in plain text
        :return: User ID
        """
        return self.__db.get_user_id(username)

    def get_user_password(self, user_id: int) -> str:
        """
        Get a user password
        :param user_id: User ID
        :return: User password
        """
        return self.__db.get_user_password(user_id)


class AuthHelper:
    def __init__(self, db: DatabaseManager) -> None:
        self.__db: DatabaseManager = db

    def access_token_expired(self, user_id: int) -> bool:
        """
        Check if the access token is expired
        :param user_id: User ID
        :return: True if expired, False otherwise
        """
        expires_at: str = self.__db.get_expiration_time(user_id)
        return StringUtils.is_after_expiration_time(expires_at)

    def correct_api_credentials_refresh(self, user_id: str, refresh_token: str) -> Tuple[bool, str]:
        """
        Check if the API credentials are correct
        :param user_id: User ID casted to string
        :param refresh_token: Refresh token
        :return: True if correct, False otherwise
        """

        if StringUtils.is_empty(user_id):
            return False, 'User ID is empty'

        if StringUtils.is_empty(refresh_token):
            return False, 'Refresh token is empty'

        user_id: int = int(user_id)

        if not self.__db.user_id_exists(user_id):
            return False, 'Invalid User ID'

        db_refresh_token: str = self.__db.get_refresh_token_by_user_id(user_id)
        if not refresh_token == db_refresh_token:
            return False, 'Refresh token is invalid'
        return True, ''

    def correct_api_credentials(self, user_id: str, access_token: str) -> Tuple[bool, str]:
        """
        Check if the API credentials are correct
        :param user_id: User ID casted to string
        :param access_token: Access token
        :return: True if correct, False otherwise
        """

        if StringUtils.is_empty(user_id):
            return False, 'User ID is empty'

        if StringUtils.is_empty(access_token):
            return False, 'Access token is empty'

        user_id: int = int(user_id)

        if not self.__db.user_id_exists(user_id):
            return False, 'Invalid User ID'

        db_access_token: str = self.__db.get_access_token_by_user_id(user_id)
        if not access_token == db_access_token:
            return False, 'Access token is invalid'
        return True, ''
