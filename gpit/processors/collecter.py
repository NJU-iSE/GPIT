import os
from abc import abstractmethod

from gpit.utils.utils import write_to_file, get_response_data
import csv
import time
from gpit.utils.logging import COL_LOG, ClE_LOG, COU_LOG, logging



class Collector:
    def __init__(self, access_token, repos_name: str = None, query=None, variables=None, to_file=None,
                 url="https://api.github.com/graphql", headers=None,
                 **kwargs):
        if headers is None:
            self.headers = {
                "Authorization": f"Bearer {access_token}"
            }
        else:
            self.headers = headers
        self.repos_name = repos_name
        self.url = url
        self.query = query
        self.variables = variables
        self.to_file = to_file
        if not os.path.exists(os.path.dirname(to_file)):
            os.makedirs(os.path.dirname(to_file))

    
    @abstractmethod
    def get_whole_data(self):
        raise NotImplementedError

    def get_open_issues(self):
        raise NotImplemented

    def get_close_issues(self):
        raise NotImplemented


class PRCollector(Collector):
    def get_whole_data(self):
        pass


class IssueCollector(Collector):
    def __init__(self, access_token, repos_name: str = None, query=None, variables=None, to_file=None,
                 url="https://api.github.com/graphql", headers=None, **kwargs):
        super().__init__(access_token, repos_name, query, variables, to_file, url, headers, **kwargs)

    def get_whole_data(self):
        start_col_time = time.time()
        with open(self.to_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Body", "Code", "CreatedDate", "Tags", "State", "Reactions",
                             "Comments", 'Link'])  # Add "Reactions" 和 "Comments" column

            # issues = self.data["data"]["repository"]["issues"]
            # all_issues = issues["nodes"]
            # has_next_page = issues["pageInfo"]["hasNextPage"]
            # end_cursor = issues["pageInfo"]["endCursor"]

            issue_number = 0
            while issue_number == 0 or has_next_page:
                data, total_issue_count = get_response_data(self.url, self.query, self.headers, self.variables)
                issue_number += 100
                issues = data["data"]["repository"]["issues"]
                all_issues = issues["nodes"]
                has_next_page = issues["pageInfo"]["hasNextPage"]
                end_cursor = issues["pageInfo"]["endCursor"]
                self.variables["cursor"] = end_cursor
                write_to_file(all_issues, self.repos_name, writer)
                if issue_number < total_issue_count:
                    collect_rate = issue_number / total_issue_count
                else:
                    collect_rate = 1
                current_col_time = time.time()
                col_time = current_col_time - start_col_time
                COL_LOG.info(
                    f"gpit have collected and wrote {issue_number} issues into csv! {collect_rate:.2%} completed! {col_time:.2}ms")