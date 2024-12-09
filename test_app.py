import unittest
from app import app
from flask import json
import os
from dotenv import load_dotenv

load_dotenv()
TEST_JWT_TOKEN = os.getenv("TEST_JWT_TOKEN")

class TestInvoiceAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test client and any required test data."""
        self.app = app.test_client()
        self.app.testing = True
        self.auth_headers = {
            "Authorization": f"Bearer {TEST_JWT_TOKEN}"
        }

    def test_get_invoices(self):
        """Test retrieving all invoices without any filters."""
        response = self.app.get('/invoices', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)  # Ensure the response is a list of invoices

    def test_unauthorized_access(self):
        """Test accessing endpoint without a JWT token."""
        response = self.app.get('/invoices')
        self.assertEqual(response.status_code, 401)  # Unauthorized

if __name__ == "__main__":
    unittest.main()
