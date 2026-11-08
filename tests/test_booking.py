import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from my_tool.core.booking import ConflictError, ValidationError
from my_tool.db import cancel_booking, create_booking, init_db, list_bookings, list_labs


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "lab.db"
        init_db(self.db)
        self.lab_id = list_labs(self.db)[0]["id"]

    def item(self, **changes):
        item = {
            "lab_id": self.lab_id,
            "requester": "张同学",
            "purpose": "课程实验",
            "participants": 12,
            "start": "2026-11-09T09:00",
            "end": "2026-11-09T10:00",
        }
        item.update(changes)
        return item

    def test_create_and_cancel(self):
        booked = create_booking(self.db, self.item())
        self.assertEqual(booked["lab_name"], "软件工程实验室 A101")
        self.assertEqual(len(list_bookings(self.db)), 1)
        self.assertTrue(cancel_booking(self.db, booked["id"]))
        self.assertFalse(cancel_booking(self.db, booked["id"]))
        self.assertEqual(list_bookings(self.db), [])

    def test_overlap_rejected_but_adjacent_allowed(self):
        create_booking(self.db, self.item())
        with self.assertRaises(ConflictError):
            create_booking(self.db, self.item(start="2026-11-09T09:30", end="2026-11-09T10:30"))
        create_booking(self.db, self.item(start="2026-11-09T10:00", end="2026-11-09T11:00"))
        self.assertEqual(len(list_bookings(self.db)), 2)

    def test_invalid_capacity_and_time(self):
        for item in (
            self.item(participants=31),
            self.item(start="2026-11-09T07:00"),
            self.item(end="2026-11-09T14:00"),
            self.item(end="2026-11-10T10:00"),
        ):
            with self.subTest(item=item), self.assertRaises(ValidationError):
                create_booking(self.db, item)
        self.assertEqual(list_bookings(self.db), [])


if __name__ == "__main__":
    unittest.main()

