import sqlite3 as sqlite
import string
from typing import *
from dataclasses import dataclass


@dataclass
class Note:
    id: int
    subject: str
    note: str
    user_id: int
    weight: float  # how much the note counts
    release_date: str  # when teacher gave the note
    created_at: str  # when the note was inserted into the database

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'subject': self.subject,
            'note': self.note,
            'user_id': self.user_id,
            'weight': self.weight,
            'release_date': self.release_date,
            'created_at': self.created_at
        }


@dataclass
class Subject:
    name: str
    notes: List[Note]
    gpa: float

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'note_count': len(self.notes),
            'gpa': self.gpa
        }


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_at: str


@dataclass
class UserInfo:
    token_info: TokenPair
    user_id: int


class DatabaseManager:
    def __init__(self, string_helper, db: str = 'MyNotes') -> None:
        self.__db: sqlite.Connection = sqlite.connect(db, check_same_thread=False)
        self.__cursor: sqlite.Cursor = self.__db.cursor()

        self.__string_helper = string_helper

        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )""")

        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            note TEXT NOT NULL,
            note_owner INTEGER NOT NULL,
            release_date TEXT DEFAULT '',
            weight FLOAT DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_owner) REFERENCES users(id)
        )""")

        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            access_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            refresh_token TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")

        self.__db.commit()

        self.__default_expiration_time: int = 60 * 60 * 24 * 30  # 30 days
        self.__token_length: int = 32
        self.__token_chars: str = string.ascii_letters + string.digits + '_!@#'

    def __del__(self) -> None:
        self.__db.close()

    def generate_access_token(self, user_id: int) -> TokenPair:
        """
        Generate an access token
        :param user_id: User ID
        :return: Access token
        """
        access_token: str = self.__string_helper.generate_token(self.__token_length, self.__token_chars)
        refresh_token: str = self.__string_helper.generate_token(self.__token_length, self.__token_chars)
        expires_at: str = self.__string_helper.generate_expiration_time(self.__default_expiration_time)

        self.__cursor.execute(
            """INSERT INTO tokens (access_token, expires_at, refresh_token, user_id) VALUES (?, ?, ?, ?)""",
            (access_token, expires_at, refresh_token, user_id))
        self.__db.commit()

        return TokenPair(access_token, refresh_token, expires_at)

    def user_id_exists(self, user_id: int) -> bool:
        """
        Check if a user ID exists
        :param user_id: User ID
        :return: True if exists, False otherwise
        """
        self.__cursor.execute("""SELECT id FROM users WHERE id = ? LIMIT 1""", (user_id,))
        return self.__cursor.fetchone() is not None

    def get_access_token_by_user_id(self, user_id: int) -> str:
        """
        Get an access token by user id
        :param user_id: User ID
        :return: Access token
        """
        self.__cursor.execute("""SELECT access_token FROM tokens WHERE user_id = ? LIMIT 1""", (user_id,))
        return self.__cursor.fetchone()[0]

    def get_token_pair(self, user_id: int) -> TokenPair:
        """
        Get a token pair
        :param user_id: User ID
        :return: Token pair
        """
        self.__cursor.execute("""SELECT access_token, refresh_token, expires_at FROM tokens WHERE user_id = ?""",
                              (user_id,))
        return TokenPair(*self.__cursor.fetchone())

    def add_user(self, username: str, password: str) -> UserInfo:
        """
        Add a user to the database
        :param username: Plain text username
        :param password: Hashed password
        :return: UserInfo object
        """
        self.__cursor.execute("""INSERT INTO users (username, password) VALUES (?, ?)""", (username, password))
        self.__db.commit()

        user_id: int = self.__cursor.lastrowid
        token_info: TokenPair = self.generate_access_token(user_id)

        return UserInfo(token_info, user_id)

    def get_note_by_id(self, user_id: int, note_id: int) -> Note:
        """
        Get note information
        :param user_id: User ID
        :param note_id: Note ID
        :return: Note object
        """
        self.__cursor.execute(
            """SELECT subject, note, note_owner, release_date, weight, created_at FROM notes WHERE id = ? AND 
            note_owner = ?""",
            (note_id, user_id))
        row: Tuple = self.__cursor.fetchone()

        note_owner: int = row[2]
        if note_owner != user_id:
            raise ValueError('Note does not belong to user')

        note: Note = Note(
            id=note_id,
            subject=row[0],
            note=row[1],
            user_id=row[2],
            release_date=row[3],
            weight=row[4],
            created_at=row[5]
        )
        return note

    def username_exists(self, username: str) -> bool:
        """
        Check if a username exists
        :param username: Username to check in plain text
        :return: True if username exists, False otherwise
        """
        self.__cursor.execute("""SELECT id FROM users WHERE username = ? LIMIT 1""", (username,))
        return self.__cursor.fetchone() is not None

    def get_user_id(self, username: str) -> int:
        """
        Get a user ID
        :param username: Username in plain text
        :return: User ID
        """
        self.__cursor.execute("""SELECT id FROM users WHERE username = ? LIMIT 1""", (username,))
        return self.__cursor.fetchone()[0]

    def get_user_password(self, user_id: int) -> str:
        """
        Get a user password
        :param user_id: User ID
        :return: Password
        """
        self.__cursor.execute("""SELECT password FROM users WHERE id = ? LIMIT 1""", (user_id,))
        return self.__cursor.fetchone()[0]

    def add_note(self, subject: str, note: int, user_id: int, release_date: str = '', weight: float = 1.0) -> int:
        """
        Add a note to the database
        :param subject: Subject
        :param note: Note
        :param user_id: User ID
        :param release_date: Release date
        :param weight: Weight of the note (how much it counts)
        :return: Note ID
        """
        self.__cursor.execute(
            """INSERT INTO notes (subject, note, note_owner, release_date, weight) VALUES (?, ?, ?, ?, ?)""",
            (subject, note, user_id, release_date, weight))
        self.__db.commit()

        return self.__cursor.lastrowid

    def get_subject(self, user_id: int, subject: str) -> Subject:
        """
        Get a subject
        :param user_id: User ID
        :param subject: Subject name
        :return: Subject object
        """
        self.__cursor.execute(
            """SELECT id, note, weight, release_date, created_at FROM notes WHERE note_owner = ? AND subject = ?""",
            (user_id, subject))
        notes: List[Note] = [Note(
            id=note[0],
            subject=subject,
            note=note[1],
            user_id=user_id,
            weight=note[2],
            release_date=note[3],
            created_at=note[4]
        ) for note in self.__cursor.fetchall()]

        gpa: float = self.__calculate_gpa(notes)

        return Subject(
            name=subject,
            notes=notes,
            gpa=gpa
        )

    @staticmethod
    def __calculate_gpa(notes: List[Note]) -> float:
        """
        Calculate the GPA of a subject
        :param notes: List of notes
        :return: GPA
        """
        total_weight: float = sum([note.weight for note in notes])
        total_weighted_note: float = sum([float(note.note) * note.weight for note in notes])

        return total_weighted_note / total_weight

    def get_all_subjects(self, user_id: int) -> List[Subject]:
        """
        Get all notes for a user
        :param user_id: User ID
        :return: List of subjects
        """
        self.__cursor.execute("""SELECT DISTINCT subject FROM notes WHERE note_owner = ?""", (user_id,))
        subjects: List[str] = [subject[0] for subject in self.__cursor.fetchall()]

        return [self.get_subject(user_id, subject) for subject in subjects]
