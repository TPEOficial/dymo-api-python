import unittest
from dymoapi import DymoAPI

class TestDymoAPI(unittest.TestCase):
    def setUp(self):
        self.config = {
            # "api_key": "PRIVATE_TOKEN_HERE"
        }
        self.client = DymoAPI(self.config)
    
    def test_features(self):
        print(self.client.new_url_encrypt("https://dymo.tpeoficial.com").encrypt)

if __name__ == "__main__": unittest.main()