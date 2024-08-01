import unittest
from dymoapi import DymoAPI

class TestDymoAPI(unittest.TestCase):
    def setUp(self):
        self.config = {
            "api_key": "PRIVATE_TOKEN_HERE"
        }
        self.client = DymoAPI(self.config)

    def test_print_label(self):
        with self.assertLogs(level="INFO") as log:
            self.client.print_label("Test Label")
            self.assertIn("Printing label with text: Test Label", log.output[0])

if __name__ == "__main__":
    unittest.main()