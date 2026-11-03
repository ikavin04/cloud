import json
import unittest

from app import APP_VERSION, app


class TestApplication(unittest.TestCase):
    """Tests for every public application endpoint."""

    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert b"Welcome to openshift-cicd-demo!" in response.data

    def test_health(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.is_json
        assert json.loads(response.data) == {"status": "healthy"}

    def test_version(self):
        response = self.client.get("/version")
        assert response.status_code == 200
        assert response.is_json
        assert json.loads(response.data) == {"version": APP_VERSION}
