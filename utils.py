import pandas as pd
import yaml


def load_config_file(filepath: str):
    """Loads a YAML configuration file."""
    with open(filepath, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def get_csv_content(filepath, **kwargs):
    pass
