import argparse
import json
import unittest
from unittest.mock import patch
import rs_builder


class TestRetrofitStrategy(unittest.TestCase):

    @patch('retrofit_strategy.argparse.ArgumentParser.parse_args')
    def test_galveston(self, mock_parse_args):
        mock_args = {
            'rules': json.dumps({
                "testbed": "galveston",
                "rules": 3,
                "zones": ["1P", "1P", "0.2P"],
                "strtypes": ["1", "2", "1"],
                "pcts": [1, 1, 1]
            }),
            'retrofits': json.dumps({
                "ret_keys": ["elevation", "elevation", "elevation"],
                "ret_vals": [5, 10, 5]
            }),
            'result_name': 'Galveston 3 rules 1 percent',
            'token': 'replace with your bearer token',
            'service_url': 'https://incore-dev.ncsa.illinois.edu'
        }

        # Mock the return value of parse_args to be an object with attributes matching your arguments
        mock_parse_args.return_value = argparse.Namespace(**mock_args)
        rs_builder.main()

    @patch('retrofit_strategy.argparse.ArgumentParser.parse_args')
    def test_slc(self, mock_parse_args):
        mock_args = {
            'rules': json.dumps({
                "testbed": "slc",
                "rules": 3,
                "zones": ["COUNCIL DISTRICT 1", "COUNCIL DISTRICT 2", "COUNCIL DISTRICT 3"],
                "strtypes": ["URML", "URMM", "URML"],
                "pcts": [10, 20, 20]
            }),
            'retrofits': json.dumps({
                "ret_keys": ["Wood or Metal Deck Diaphragms Retrofitted", "Wood or Metal Deck Diaphragms Retrofitted",
                             "Wood or Metal Deck Diaphragms Retrofitted"],
                "ret_vals": ["", "", ""]
            }),
            'result_name': 'SLC 3 rules 10 20 10 percent',
            'token': 'replace with your bearer token',
            'service_url': 'https://incore-dev.ncsa.illinois.edu'
        }

        # Mock the return value of parse_args to be an object with attributes matching your arguments
        mock_parse_args.return_value = argparse.Namespace(**mock_args)
        rs_builder.main()


if __name__ == '__main__':
    unittest.main()
