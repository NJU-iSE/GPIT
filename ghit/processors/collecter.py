import os
from ghit.utils.utils import write_to_file, get_response_data
import csv
import time
from ghit.utils.logging import COL_LOG, ClE_LOG, COU_LOG


class Collector:
    def __init__(self, access_token, repos_name: str = None, query=None, to_file=None,
                 url="https://api.github.com/graphql", headers=None,
                 **kwargs):
        if headers is None:
            self.headers = {
                "Authorization": f"Bearer {access_token}"
            }
        else:
            self.headers = headers
        # 定义查询字符串
        self.repos_name = repos_name
        self.url = url
        self.query = query
        self.to_file = to_file
        if not os.path.exists(os.path.dirname(to_file)):
            os.makedirs(os.path.dirname(to_file))

    def get_one_page_issues(self):
        data, total_issue_count = get_response_data(self.url, self.query, self.headers, None)
        with open(self.to_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Body", "CreaDate", "Tags", "State", "Reactions",
                             "Comments", 'Link'])  # 添加 "Reactions" 和 "Comments" 列

            issues = data["data"]["repository"]["issues"]
            all_issues = issues["nodes"]
            write_to_file(all_issues, self.repos_name, writer)
        return self

    def get_whole_issues(self):
        start_col_time = time.time()
        with open(self.to_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Body", "Code", "CreaDate", "Tags", "State", "Reactions",
                             "Comments", 'Link'])  # 添加 "Reactions" 和 "Comments" 列

            # issues = self.data["data"]["repository"]["issues"]
            # all_issues = issues["nodes"]
            # has_next_page = issues["pageInfo"]["hasNextPage"]
            # end_cursor = issues["pageInfo"]["endCursor"]

            issue_number = 0
            end_cursor = None
            while issue_number == 0 or has_next_page:
                data, total_issue_count = get_response_data(self.url, self.query, self.headers, end_cursor)
                issue_number += 100
                issues = data["data"]["repository"]["issues"]
                all_issues = issues["nodes"]
                has_next_page = issues["pageInfo"]["hasNextPage"]
                end_cursor = issues["pageInfo"]["endCursor"]
                write_to_file(all_issues, self.repos_name, writer)
                if issue_number < total_issue_count:
                    collect_rate = issue_number / total_issue_count
                else:
                    collect_rate = 1
                current_col_time = time.time()
                col_time = current_col_time - start_col_time
                COL_LOG.info(
                    f"ghit have collected and wrote {issue_number} issues into csv! {collect_rate:.2%} completed! {col_time:.2}ms")
        return self

    def get_open_issues(self):
        raise NotImplemented

    def get_close_issues(self):
        raise NotImplemented
