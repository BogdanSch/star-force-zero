import sqlite3
from data.score import Score

class ScoreRepository:
    def __init__(self, dbPath: str):
        self.dbPath = dbPath
    def addScore(self, score: Score):
        with sqlite3.connect(self.dbPath) as connection:
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO scores (PlayerName, Score, CreatedAt) VALUES (?, ?, ?)",
                (score.playerName, score.score, score.createdAt)
            )

            connection.commit()
            cursor.close()