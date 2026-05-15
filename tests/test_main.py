import unittest
from unittest.mock import patch
from src.db.__main__ import main


class TestMain(unittest.TestCase):
    @patch('src.db.__main__.BookTUI.run')
    def test_main_runs(self, mock_run):
        main()
        mock_run.assert_called_once()
