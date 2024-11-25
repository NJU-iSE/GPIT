from typing import List


class Cleaner:
    def __init__(self, from_file: str = None):
        self.file = from_file

    def clear(self, to_file: str = None, save_col: List[str] = None, **kwargs):
        import pandas as pd
        from functools import reduce
        import operator

        df = pd.read_csv(self.file)

        years = kwargs.get("years", None)
        tags = kwargs.get("tags", None)
        keywords = kwargs.get("keywords", None)

        conditions = []

        if years:
            conditions.append(df['CreaDate'].str.startswith(years))
        if tags:
            conditions.append(df['Tags'].str.contains(tags, case=False, na=False))
        if keywords:
            conditions.append(df['Body'].str.contains(keywords, case=False, na=False))

        if conditions:
            combined_condition = reduce(operator.and_, conditions)
            filter_df = df[combined_condition]
        else:
            filter_df = df

        if save_col is not None:
            filter_df = filter_df[save_col]

        filter_df.to_csv(f'{to_file}', index=False)