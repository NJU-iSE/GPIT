from ghit.collector.tools import Collector, Cleaner, Counter
import logging
import hydra
from omegaconf import DictConfig, OmegaConf
import yaml
from jinja2 import Template

logging.basicConfig(level=logging.INFO)


@hydra.main(version_base=None, config_path="./config", config_name="config")
def collect(cfg: DictConfig):
    collector = Collector(cfg['access_token'], repos_name=cfg['repos_name'], query=cfg['query']['body'])
    collector.get_whole_issues(cfg['collect']['to_file'])


@hydra.main(version_base=None, config_path="./config", config_name="config")
def count(cfg: DictConfig):
    counter = Counter(cfg['count']['from_file'])
    df = counter.prio_rank({"Comments": 1}, 1000)

    df.to_csv("./results/mindspore_filter_rank.csv")


@hydra.main(version_base=None, config_path="./config", config_name="config")
def clean(cfg: DictConfig):
    cleaner = Cleaner(cfg['clean']['from_file'])
    cleaner.clear(cfg['clean']['to_file'])
    print('finsh')


if __name__ == '__main__':
    # collect()
    clean()