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
    def getTop(self, number: int) -> list[Score]:
        with sqlite3.connect(self.dbPath) as connection:
            cursor = connection.cursor()

            scores = cursor.execute(
                "SELECT PlayerName, Score, CreatedAt FROM scores ORDER BY Score DESC, CreatedAt ASC"
            ).fetchmany(number)

            connection.commit()
            cursor.close()
        return [Score(row[0], row[1], row[2]) for row in scores]