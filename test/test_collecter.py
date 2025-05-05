import unittest
from unittest.mock import patch, mock_open, MagicMock
from gpit.processors.collecter import IssueCollector
import csv
import time

class TestCollector(unittest.TestCase):
    # FIXME@SHAOYU: Not sure whether I should separate this test from some external dependencies.
    @patch('gpit.processors.collecter.get_response_data')
    @patch('gpit.processors.collecter.write_to_file')
    @patch('gpit.utils.logging.COL_LOG')
    def test_get_whole_issues(self, mock_col_log, mock_write_to_file, mock_get_response_data):
        # 设置模拟数据
        mock_get_response_data.return_value = ({
            "data": {
                "repository": {
                    "issues": {
                        "nodes": [
                            {"title": "Issue 1", "body": "Body 1", "createdAt": "2023-01-01", "state": "open", "labels": {"nodes": [{"name": "bug"}]}, "reactions": {"totalCount": 5}, "comments": {"totalCount": 10}, "number": 1}
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"}
                    }
                }
            }
        }, 1)

        # 设置 IssueCollector
        collector = IssueCollector()
        collector.to_file = 'test_issues.csv'
        collector.url = 'https://api.github.com/graphql'
        collector.query = 'test_query'
        collector.query_type = 'issue'
        collector.headers = {'Authorization': 'Bearer token'}
        collector.variables = {'cursor': None}
        collector.repos_name = 'test_repo'

        # 调用方法
        collector.get_whole_data()

        # 验证
        mock_get_response_data.assert_called_once_with(
            collector.url, collector.query, collector.query_type, collector.headers, collector.variables
        )
        mock_write_to_file.assert_called_once()
        mock_col_log.info.assert_called_once_with(
            "gpit have collected and wrote 100 issues into csv! 100.00% completed! 0.0ms"
        )

if __name__ == '__main__':
    unittest.main()
