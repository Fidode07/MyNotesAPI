from flask import Flask, jsonify, Response, request
from flask_classful import FlaskView, route

from ext.database_manager import DatabaseManager


class TestView(FlaskView):

    @route('/add_note', methods=['GET'])
    def add_note(self) -> Response:
        """
        Add a note
        :return: Response
        """
        database: DatabaseManager = DatabaseManager()

        data = request.args
        subject: str = data.get('subject')
        note: int = int(data.get('note'))
        user_id: int = int(data.get('user_id'))
        release_date: str = data.get('release_date')
        weight: float = float(data.get('weight'))

        note_id: int = database.add_note(
            subject=subject,
            note=note,
            user_id=user_id,
            release_date=release_date,
            weight=weight
        )

        return jsonify({
            'status': 'success',
            'message': 'Note added successfully',
            'note_id': note_id
        })


class FlaskHelper:
    def __init__(self) -> None:
        self.__app = Flask(__name__)
        TestView.register(self.__app, route_base='/')

    def run(self) -> None:
        self.__app.run(debug=True)
