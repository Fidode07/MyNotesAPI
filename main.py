from ext.flask_server import FlaskServer


def main() -> None:
    server: FlaskServer = FlaskServer(debug=True)
    server.run()


if __name__ == '__main__':
    main()
