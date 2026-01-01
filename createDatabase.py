import sqlite3
from sqlite3 import Cursor
from config import DB_PATH

def main():
    connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = connection.cursor()

    cursor.execute("""
        Create Table If Not Exists Scores (
            Id Integer Primary Key AUTOINCREMENT,
            PlayerName Text NOT NULL,
            Score Integer NOT NULL,
            CreatedAt Text NOT NULL
        );
    """)

if __name__ == "__main__":
    main()