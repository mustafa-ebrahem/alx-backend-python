#!/usr/bin/env python3
"""Unit tests for client module functions and classes."""

from unittest import TestCase
from unittest.mock import patch, PropertyMock
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

    @patch.object(GithubOrgClient, 'org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test GithubOrgClient._public_repos_url returns the expected URL."""
        # Define the known payload with repos_url
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Set up the mock return value
        mock_org.return_value = known_payload

        # Create client instance
        client = GithubOrgClient("google")

        # Test that _public_repos_url returns the expected URL
        result = client._public_repos_url
        self.assertEqual(result, known_payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repo list."""
        # Define the payload that get_json should return
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        mock_get_json.return_value = test_payload

        # Use patch as context manager to mock _public_repos_url
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/test"

            # Create client instance and call public_repos
            client = GithubOrgClient("test")
            result = client.public_repos()

            # Expected result should be list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            # Assert that _public_repos_url was called once
            mock_repos_url.assert_called_once()

        # Assert that get_json was called once
        mock_get_json.assert_called_once()
