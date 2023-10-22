import sqlite3 as sqlite
from typing import *
from dataclasses import dataclass


@dataclass
class Note:
    subject: str
    note: str
    user_id: int
    weight: int  # how much the note counts
    release_date: str  # when teacher gave the note
    created_at: str  # when the note was inserted into the database


@dataclass
class Subject:
    name: str
    notes: List[Note]
    gpa: float


class DatabaseManager:
    def __init__(self, db: str = 'MyNotes') -> None:
        self.__db: sqlite.Connection = sqlite.connect(db)
        self.__cursor: sqlite.Cursor = self.__db.cursor()

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

        self.__db.commit()

    def __del__(self) -> None:
        self.__db.close()

    def add_user(self, username: str, password: str) -> int:
        """
        Add a user to the database
        :param username: Plain text username
        :param password: Hashed password (sha256)
        :return: User ID
        """
        self.__cursor.execute("""INSERT INTO users (username, password) VALUES (?, ?)""", (username, password))
        self.__db.commit()

        return self.__cursor.lastrowid

    def get_note_information(self, note_id: int) -> Tuple[str, str, int, str]:
        """
        Get note information
        :param note_id: Note ID
        :return: Subject, note, user ID
        """
        self.__cursor.execute("""SELECT subject, note, note_owner, FROM notes WHERE id = ?""", (note_id,))
        return self.__cursor.fetchone()

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
