import flask.json
from flask import Flask, jsonify, Response
from flask_classful import FlaskView, route
from ext.utils import *
from ext.database_manager import DatabaseManager, UserInfo, TokenPair, Subject
from typing import *


class MyNotes(FlaskView):
    def __init__(self):
        super().__init__()
        self.__db: DatabaseManager = DatabaseManager(StringUtils)
        self.__hasher: Hasher = Hasher(algorithm='sha512')
        self.__login_utils: LoginUtils = LoginUtils(self.__db, self.__hasher)
        self.__auth_helper: AuthHelper = AuthHelper(self.__db)

    @route('/add_note', methods=['POST'])
    def add_note(self) -> tuple[Response, int]:
        """
        Add a note to the database
        :return: Response and status code
        """
        try:
            user_id: str = str(flask.request.json['user_id'])
            access_token: str = str(flask.request.json['access_token'])

            auth_correct: Tuple[bool, str] = self.__auth_helper.correct_api_credentials(user_id, access_token)

            if not auth_correct[0]:
                raise InvalidArgumentException(auth_correct[1])

            user_id: int = int(user_id)

            subject: str = str(flask.request.json['subject'])
            note: int = int(flask.request.json['note'])
            weight: float = float(flask.request.json['weight'])
            release_date: str = str(flask.request.json['release_date'])

            self.__db.add_note(subject=subject, note=note, user_id=user_id, release_date=release_date, weight=weight)
            return jsonify({
                'status': 200,
                'error': False
            }), 200
        except Exception as e:
            return jsonify({'status': 500, 'error': True, "error_msg": str(e)}), 500

    @route('/get_subject', methods=['POST'])
    def get_subject(self) -> tuple[Response, int]:
        """
        Get a subject
        :return: Response and status code
        """
        try:
            user_id: str = str(flask.request.json['user_id'])
            access_token: str = str(flask.request.json['access_token'])

            auth_correct: Tuple[bool, str] = self.__auth_helper.correct_api_credentials(user_id, access_token)

            if not auth_correct[0]:
                raise InvalidArgumentException(auth_correct[1])

            user_id: int = int(user_id)

            subject: str = str(flask.request.json['subject'])
            subject: Subject = self.__db.get_subject(user_id, subject)

            return jsonify({
                'status': 200,
                'error': False,
                'subject': subject.to_json(),
                'notes': [x.to_json() for x in subject.notes]
            }), 200

        except Exception as e:
            return jsonify({'status': 500, 'error': True, "error_msg": str(e)}), 500

    @route('/get_subjects', methods=['POST'])
    def get_subjects(self) -> tuple[Response, int]:
        """
        Get all subjects of a user
        :return: Response and status code
        """
        try:
            user_id: str = str(flask.request.json['user_id'])
            access_token: str = str(flask.request.json['access_token'])

            auth_correct: Tuple[bool, str] = self.__auth_helper.correct_api_credentials(user_id, access_token)

            if not auth_correct[0]:
                raise InvalidArgumentException(auth_correct[1])

            user_id: int = int(user_id)

            subjects: List[Subject] = self.__db.get_all_subjects(user_id)
            return jsonify({
                'status': 200,
                'error': False,
                'subjects': [x.to_json() for x in subjects]
            }), 200
        except Exception as e:
            return jsonify({'status': 500, 'error': True, "error_msg": str(e)}), 500

    # TODO: Implement refresh token

    @route('/login', methods=['POST'])
    def login_user(self) -> tuple[Response, int]:
        """
        Login a user
        :return: Response and status code
        """
        # If the user has given the correct credentials we generate an access token
        # and return it to the user
        try:
            username: CheckedParameter = StringUtils.validate_username(flask.request.json['username'])
            password: str = flask.request.json['password']

            if StringUtils.is_empty(password):
                print('Password is empty')
                raise InvalidArgumentException('Password or Username is incorrect')

            salted_password: str = StringUtils.add_salt_to_hashed_password(password, self.__hasher)

            if not username.valid:
                raise InvalidArgumentException(username.message)

            if not self.__login_utils.username_exists(username.parameter):
                print('Username does not exist')
                raise InvalidArgumentException('Password or Username is incorrect')

            user_id: int = self.__login_utils.get_user_id(username.parameter)
            db_password: str = self.__login_utils.get_user_password(user_id)

            if not self.__hasher.equal_hashes(salted_password, db_password):
                print('Password is incorrect')
                raise InvalidArgumentException('Password or Username is incorrect')

            # everything is fine, we can return the tokens
            token_pair: TokenPair = self.__db.get_token_pair(user_id)

            return jsonify({
                'status': 200,
                'error': False,
                'access_token': token_pair.access_token,
                'refresh_token': token_pair.refresh_token,
                'expires_at': token_pair.expires_at,
                'user_id': user_id
            }), 200
        except Exception as e:
            return jsonify({'status': 500, 'error': True, "error_msg": str(e)}), 500

    @route('/register', methods=['POST'])
    def register_user(self) -> tuple[Response, int]:
        """
        Register a new user
        :return: Response and status code
        """
        try:
            username: CheckedParameter = StringUtils.validate_username(flask.request.json['username'])
            password: CheckedParameter = StringUtils.validate_password(flask.request.json['password'], self.__hasher)

            if self.__db.username_exists(username.parameter):
                raise InvalidArgumentException('Username already exists')

            if not username.valid:
                raise InvalidArgumentException(username.message)

            if not password.valid:
                raise InvalidArgumentException(password.message)

            # password.parameter is already a hashed salted password
            user: UserInfo = self.__db.add_user(username=username.parameter,
                                                password=password.parameter)
            return jsonify({
                'status': 200,
                'error': False,
                'access_token': user.token_info.access_token,
                'refresh_token': user.token_info.refresh_token,
                'expires_at': user.token_info.expires_at,
                'user_id': user.user_id
            }), 200
        except Exception as e:
            return jsonify({'status': 500, 'error': True, "error_msg": str(e)}), 500


class FlaskServer:
    def __init__(self, debug: bool = False) -> None:
        self.__app: Flask = Flask(__name__)
        MyNotes.register(self.__app, route_base='/')
        self.debug: bool = debug

    def run(self) -> None:
        self.__app.run(debug=self.debug)
