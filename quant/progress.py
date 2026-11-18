"""Local, shared attempt history for the browser and terminal."""
import os
import sqlite3
from contextlib import closing
from pathlib import Path


def connect():
    location = Path(os.environ.get("QUANT_PRACTICE_DB") or
                    Path(os.environ.get("LOCALAPPDATA", Path.home())) / "QuantPractice" / "progress.sqlite3")
    location.parent.mkdir(exist_ok=True, parents=True)
    db = sqlite3.connect(location, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS attempts (
        seq INTEGER PRIMARY KEY, token TEXT UNIQUE, topic TEXT, mode TEXT, seed INTEGER,
        correct INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return db


def record(token, topic, mode, seed, correct):
    with closing(connect()) as db, db:
        db.execute("INSERT OR IGNORE INTO attempts(token,topic,mode,seed,correct) VALUES(?,?,?,?,?)",
                   (token, topic, mode, seed, int(correct)))


def history():
    with closing(connect()) as db:
        return {(r["topic"], r["mode"]): dict(r) for r in db.execute("""
            SELECT a.topic,a.mode,a.seed,a.correct,s.tries,s.misses FROM attempts a
            JOIN (SELECT topic, mode, MAX(seq) AS latest, COUNT(*) AS tries,
                         SUM(1-correct) AS misses FROM attempts GROUP BY topic,mode) s
            ON a.seq=s.latest""")}
