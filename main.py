import fire
import re
import operator
import pandas as pd

from typing import Union, List
from functools import reduce
from pathlib import Path

from gpit.utils.utils import load_config_file
from gpit.processors import collecter, counter


class Pipeline(object):
    def __init__(
        self,
        repo_path=None,
        config_file="config/config.yaml",
        github_pat_token_file="config/github_pat.txt"
    ):
        self.repo_path = repo_path
        self.config = load_config_file(config_file)
        self.github_pat_token_file = github_pat_token_file

    def run_collection(
        self,
        query_type,
    ):
        access_tokens = Path(self.github_pat_token_file).read_text().strip()
        assert query_type in ["issue", "PR"], f"query_type must be 'query' or 'issues' but got {query_type}"
        # TLDR@SHAOYU; Currently, PR query and issue query are compatible.
        # Maybe PR query can be extended to include file changes.
        if query_type == "issue":
            query = self.config['query']["issue_query"]
        elif query_type == "PR":
            query = self.config['query']["pr_query"]


        variables = {
            "cursor": None,
            "owner": self.repo_path.split("/")[0],
            "name": self.repo_path.split("/")[1]
        }

        if query_type == "issue":
            cor = collecter.IssueCollector(access_tokens, repos_name=self.repo_path, query_type=query_type, query=query, variables=variables,
                                  to_file=f"Results/{self.repo_path.split('/')[-1]}/all_{query_type}s.csv")
        elif query_type == "PR":
            cor = collecter.PRCollector(access_tokens, repos_name=self.repo_path, query_type=query_type, query=query, variables=variables,
                                  to_file=f"Results/{self.repo_path.split('/')[-1]}/all_{query_type}s.csv")

        cor.get_whole_data()

        print("collecter is initialized successfully")



    def run_cleaning(
        self,
        query_type: str = None,
        years: Union[List[str], str] = None,
        tags: Union[List[str], str] = None,
        title_keywords: str = None,
        body_keywords: str = None,
        save_cols: List[str] = None,
    ):
        assert query_type in ["issue", "PR"], f"query_type must be 'query' or 'issues' but got {query_type}"
        file_path = f"Results/{self.repo_path.split('/')[-1]}/all_{query_type}s.csv"
        df = pd.read_csv(file_path)
        if years is not None:  # FIXME@SHAOYU: the col name should not be replaced, maybe I should not use `Year`
            df['CreatedDate'] = pd.to_datetime(df['CreatedDate'])
            df["Year"] = df['CreatedDate'].dt.year
            if isinstance(years, str):
                years = [years]

            df = df[df["Year"].isin(years)]
            if "Year" not in (save_cols or []):
                df = df.drop(columns=["Year"])

        if tags is not None:
            if isinstance(tags, str):
                tags = tags.split(", ")
            df['Tags'] = df['Tags'].fillna('').apply(lambda x: x.split(', ') if x else [])
            df = df[df['Tags'].apply(lambda x: all(tag in x for tag in tags))]


        if title_keywords is not None:
            if isinstance(title_keywords, str):
                title_keywords = [title_keywords]
            pattern = re.compile('|'.join(title_keywords), re.IGNORECASE)
            df = df[df["Title"].fillna("").apply(lambda x: bool(pattern.search(x)))]

        if body_keywords is not None:
            if isinstance(body_keywords, str):
                body_keywords = [body_keywords]
            pattern = re.compile('|'.join(body_keywords), re.IGNORECASE)
            df = df[df["Body"].fillna("").apply(lambda x: bool(pattern.search(x)))]

        if save_cols is not None:
            if not isinstance(save_cols, list):
                raise ValueError("save_col must be a list")
            missing_cols = set(save_cols) - set(df.columns)
            if missing_cols:
                raise ValueError(f"no col names: {', '.join(missing_cols)}")
            df = df[save_cols]

        df.to_csv(Path(file_path).parent / f"cleaned_{query_type}s.csv", index=False)

    def run_counting(
        self,
        draw: bool = False,
    ):
        pass

    def run_analysis(self):
        pass


if __name__ == "__main__":
    fire.Fire(Pipeline)
