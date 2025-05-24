import unittest
from unittest.mock import patch, mock_open, MagicMock
from gpit.processors.collecter import IssueCollector
import csv
import time