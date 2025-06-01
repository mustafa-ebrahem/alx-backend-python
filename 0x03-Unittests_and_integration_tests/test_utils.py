#!/usr/bin/env python3
"""Unit tests for utils module functions."""

from unittest import TestCase
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map
from utils import get_json
from utils import memoize


class TestAccessNestedMap(TestCase):
    """Test nested map access method"""
    @parameterized.expand([
        ({"a": 1}, ("a", ), 1),
        ({"a": {"b": 2}}, ("a", ), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
        ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns correct values"""
        self.assertEqual(
            access_nested_map(nested_map=nested_map, path=path),
            expected
            )

    @parameterized.expand([({}, ("a",)), ({"a": 1}, ("a", "b"))])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map=nested_map, path=path)


class TestGetJson(TestCase):
    """Test get json method"""
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    @patch("utils.requests.get")
    def test_get_json(self, url, payload, mock_get):
        """Test that get_json returns the response and calls it only once"""

        mock_response = Mock()
        mock_response.json.return_value = payload

        # mock_get is providede by the @patch decorator
        # it replaces the request.get in the utils module
        mock_get.return_value = mock_response

        # call the method to be tested
        result = get_json(url)

        # assert response
        self.assertEqual(result, payload)
        mock_get.assert_called_once_with(url)


class TestMemoize(TestCase):
    """Test utils memoize decorator"""
    def test_memoize(self):
        """Test the memoize decorator is caching as expected"""
        class TestClass:
            """A test class to use memoize test on"""
            def a_method(self):
                """Simple method that returns 42 for testing purposes."""
                return 42

            @memoize
            def a_property(self):
                """Memoized property that calls a_method."""
                return self.a_method()

        test_obj = TestClass()
        with patch.object(test_obj, 'a_method', return_value=42) as mock_methd:

            result1 = test_obj.a_property

            result2 = test_obj.a_property

            self.assertEqual(result1, 42)

            self.assertEqual(result2, 42)

            mock_methd.assert_called_once()
