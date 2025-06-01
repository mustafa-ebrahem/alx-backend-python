#!/usr/bin/env python3

from unittest import TestCase
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(TestCase):
        
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        result = access_nested_map(nested_map=nested_map, path=path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b"))
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        result = access_nested_map(nested_map=nested_map, path=path)
        self.assertRaises(result)
