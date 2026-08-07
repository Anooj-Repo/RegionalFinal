"""
Unit Tests for Flask REST APIs (tests/unit/test_unit_apis.py)
"""

import unittest
import sys
import os
import json

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

class TestBackendAPIs(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Login to get JWT Token
        res = self.client.post('/api/auth/login', json={'username': 'rohit', 'password': 'user123'})
        self.token = res.json['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_health_check(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['status'], 'healthy')

    def test_get_projects(self):
        res = self.client.get('/api/projects', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json['projects']), 5)

    def test_get_raid_items(self):
        res = self.client.get('/api/raid', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json['raid_items']), 0)

    def test_get_emails(self):
        res = self.client.get('/api/emails', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn('emails', res.json)

if __name__ == '__main__':
    unittest.main()
