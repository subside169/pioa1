import unittest
from unittest.mock import patch
from src.db.__main__ import main


class TestMain(unittest.TestCase):
    @patch('builtins.input', return_value='1')   # 1 = выбор in-memory БД
    @patch('src.db.__main__.BookTUI.run')
    def test_main_runs(self, mock_run, mock_input):
        main()
        mock_run.assert_called_once()
