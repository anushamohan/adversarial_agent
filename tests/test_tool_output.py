import sys
import unittest
from datetime import date, datetime
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cotabreak.tool_output import dumps_iso8601_json


class Status(Enum):
    READY = "ready"


class ToolOutputTest(unittest.TestCase):
    def test_serializes_datetime_date_and_enum(self) -> None:
        rendered = dumps_iso8601_json(
            {
                "starts_at": datetime(2024, 5, 15, 9, 30),
                "day": date(2024, 5, 15),
                "status": Status.READY,
            }
        )
        self.assertEqual(
            rendered,
            '{"starts_at": "2024-05-15T09:30:00", "day": "2024-05-15", '
            '"status": "ready"}',
        )

    def test_rejects_unknown_objects(self) -> None:
        with self.assertRaisesRegex(TypeError, "not JSON serializable"):
            dumps_iso8601_json({"value": object()})


if __name__ == "__main__":
    unittest.main()
