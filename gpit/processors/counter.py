import pandas as pd
from gpit.utils.utils import process_text, word_only, write_to_file, get_response_data, draw_line_chart


class Counter:
    def __init__(self, file: str):
        self.file = file
        self.df = pd.read_csv(file)

    def prio_rank(self, col_weights: dict[str, float], top_n: int = None) -> pd.DataFrame:  # need file name
        total_weight = sum(col_weights.values())  # compute the sum of all weights
        sort_key_df = pd.DataFrame()
        for col in self.df.columns:
            if col in col_weights:
                sort_key_df[col] = self.df[col] * col_weights[col]
        sort_key_df['sort_key'] = sort_key_df.sum(axis=1) / total_weight
        assert sort_key_df.__len__() != 0, f"cols in col_weights are not contained in file: {self.file}"
        df_sorted = self.df.iloc[sort_key_df['sort_key'].sort_values(ascending=False).index]

        if top_n is not None:
            df_sorted = df_sorted.head(top_n)

        return df_sorted

    def draw_counts_by_year(self):
        self.df["CreatedDate"] = pd.to_datetime(self.df["CreatedDate"], format='%Y-%m-%dT%H:%M:%SZ')
        self.df["year"] = self.df["CreatedDate"].dt.year

        year_counts = self.df.groupby("year").size()
        year_counts = year_counts.sort_index()

        draw_line_chart("PyTorch Memory Issues", "Year", "Counts", year_counts.index, year_counts.values)
