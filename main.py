import fire
import re
import operator
import pandas as pd

from typing import Union, List
from functools import reduce
from pathlib import Path

from ghit.utils.utils import load_config_file
from ghit.processors import collecter, counter


class Pipeline(object):
    def __init__(
        self,
        repo_path=None,
        config_file="config/config.yaml"
    ):
        self.repo_path = repo_path
        self.config = load_config_file(config_file)

    def run_collection(
        self,
        access_tokens,
    ):
        query = self.config['query']["body"]
        variables = {
            "cursor": None,
            "owner": self.repo_path.split("/")[0],
            "name": self.repo_path.split("/")[1]
        }
        cor = collecter.Collector(access_tokens, repos_name=self.repo_path, query=query, variables=variables,
                                  to_file=f"Results/{self.repo_path.split('/')[-1]}/all_issues.csv")
        print("collecter is initialized successfully")
        cor.get_whole_issues()

    def run_cleaning(
        self,
        years: Union[List[str], str] = None,
        tags: Union[List[str], str] = None,
        keywords: str = None,
        save_cols: List[str] = None,
        res_name: str = "cleaned_issues.csv"
    ):
        file_path = f"Results/{self.repo_path.split('/')[-1]}/all_issues.csv"
        df = pd.read_csv(file_path)

        if years is not None:
            df['CreaDate'] = pd.to_datetime(df['CreaDate'])
            df["Year"] = df['CreaDate'].dt.year
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

        if keywords is not None:
            if isinstance(keywords, str):
                keywords = [keywords]
            pattern = re.compile('|'.join(keywords), re.IGNORECASE)
            df = df[df["Body"].fillna("").apply(lambda x: bool(pattern.search(x)))]

        if save_cols is not None:
            if not isinstance(save_cols, list):
                raise ValueError("save_col must be a list")
            missing_cols = set(save_cols) - set(df.columns)
            if missing_cols:
                raise ValueError(f"no col names: {', '.join(missing_cols)}")
            df = df[save_cols]

        df.to_csv(Path(file_path).parent / res_name, index=False)

    def run_counting(
        self,
        draw: bool = False,
    ):
        pass

    def run_analysis(self):
        pass


if __name__ == "__main__":
    fire.Fire(Pipeline)
