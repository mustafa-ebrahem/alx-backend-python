#!/usr/bin/env python3
"""Unit tests for client module functions and classes."""

from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns the correct value."""
        # Set up the mock return value
        expected_org_data = {"name": org_name, "id": 12345}
        mock_get_json.return_value = expected_org_data

        # Create client instance and call org method
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert that get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert that the result matches the mocked return value
        self.assertEqual(result, expected_org_data)
