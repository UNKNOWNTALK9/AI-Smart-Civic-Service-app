import os
import tempfile
import unittest

from ai.preprocessing import clean_text
from database import DatabaseManager


class TestCore(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(clean_text(" Water!!!   Leak "), "water leak")

    def test_create_complaint(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = DatabaseManager(os.path.join(tmp, "test.db"))
            citizen_id = db.register(
                "Test Citizen", "citizen@example.com", "03000000000", "Password123"
            )
            analysis = {
                "category": "Water",
                "category_confidence": 95.0,
                "priority": "High",
                "priority_confidence": 90.0,
                "summary": "Water leak reported.",
                "department": "Water & Sanitation",
                "model_name": "test",
            }
            complaint_id = db.create_complaint(
                citizen_id, "Water leak", "A major water leak.", "Main Road", analysis
            )
            complaint = db.get_complaint(complaint_id)

            self.assertTrue(complaint_id.startswith("CIV-"))
            self.assertIsNotNone(complaint)
            self.assertEqual(complaint["citizen_id"], citizen_id)
            self.assertEqual(complaint["status"], "Open")


if __name__ == "__main__":
    unittest.main()
