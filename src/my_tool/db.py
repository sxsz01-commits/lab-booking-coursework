"""SQLite persistence for the demo booking workflow."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .core.booking import ConflictError, ValidationError, validate_booking


ROOT = Path(__file__).resolve().parents[2]


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db(path: str | Path, sample_path: str | Path | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS labs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                location TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                lab_id INTEGER NOT NULL REFERENCES labs(id),
                requester TEXT NOT NULL,
                purpose TEXT NOT NULL,
                participants INTEGER NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_booking_lab_time
                ON bookings(lab_id, start, end);
            """
        )
        if db.execute("SELECT COUNT(*) FROM labs").fetchone()[0] == 0:
            source = Path(sample_path) if sample_path else ROOT / "data" / "sample_labs.json"
            labs = json.loads(source.read_text(encoding="utf-8"))
            db.executemany(
                "INSERT INTO labs(name, capacity, location) VALUES(:name, :capacity, :location)",
                labs,
            )


def list_labs(path: str | Path) -> list[dict]:
    with closing(connect(path)) as db:
        return [dict(row) for row in db.execute("SELECT * FROM labs ORDER BY id")]


def list_bookings(path: str | Path) -> list[dict]:
    with closing(connect(path)) as db:
        rows = db.execute(
            """SELECT b.*, l.name AS lab_name FROM bookings b
               JOIN labs l ON l.id = b.lab_id ORDER BY b.start, b.id"""
        )
        return [dict(row) for row in rows]


def create_booking(path: str | Path, data: dict) -> dict:
    try:
        lab_id = int(data.get("lab_id"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValidationError("请选择实验室") from exc
    if isinstance(data.get("lab_id"), bool):
        raise ValidationError("请选择实验室")
    with closing(connect(path)) as db:
        # Serialize the conflict check and insert across concurrent requests.
        db.execute("BEGIN IMMEDIATE")
        try:
            lab = db.execute("SELECT * FROM labs WHERE id = ?", (lab_id,)).fetchone()
            if lab is None:
                raise ValidationError("实验室不存在")
            item = validate_booking(data, lab["capacity"])
            overlap = db.execute(
                """SELECT id FROM bookings WHERE lab_id = ?
                   AND start < ? AND end > ? LIMIT 1""",
                (lab_id, item["end"], item["start"]),
            ).fetchone()
            if overlap:
                raise ConflictError("该实验室的所选时段已被预约")
            cursor = db.execute(
                """INSERT INTO bookings(lab_id, requester, purpose, participants, start, end)
                   VALUES(?, ?, ?, ?, ?, ?)""",
                (lab_id, item["requester"], item["purpose"], item["participants"],
                 item["start"], item["end"]),
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        row = db.execute(
            """SELECT b.*, l.name AS lab_name FROM bookings b
               JOIN labs l ON l.id = b.lab_id WHERE b.id = ?""",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def cancel_booking(path: str | Path, booking_id: int) -> bool:
    with closing(connect(path)) as db:
        cursor = db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        return cursor.rowcount > 0

