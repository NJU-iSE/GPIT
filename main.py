from ghit.collector.tools import Collector, Cleaner, Counter
import logging
import yaml
from jinja2 import Template
import click
from utils import load_config_file

logging.basicConfig(level=logging.INFO)


def collect(access_token, repo_name, query):
    collector = Collector(access_token, repos_name=repo_name, query=query,
                          to_file=f"Results/{repo_name.split('/')[-1]}.csv")
    collector.get_whole_issues()


def count():
    pass


def clean():
    pass


@click.group()
@click.option(
    "config_file",
    "--config",
    type=str,
    default=None,
    help="Path to the configure file.",
)
@click.pass_context
def cli(ctx, config_file):
    """run the main using a configuration file"""
    if config_file is not None:
        config_dict = load_config_file(config_file)
        ctx.ensure_object(dict)
        ctx.obj["CONFIG_DICT"] = config_dict


@cli.command("main")
@click.pass_context
@click.option(
    "processor",
    "--processor",
    type=str,
    default=None,
    help="use the specific processor to do something (i.e., collector, counter, and cleaner)"
)
@click.option(
    "access_tokens",
    "--access_tokens",
    type=str,
    default=None,
    help="refer to https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
)
@click.option(
    "repo_name",
    "--repo_name",
    type=str,
    default=None,
    help="the name of the repository"
)
def main_with_config(ctx, processor, access_tokens, repo_name):
    """ Run the main using a configuration file."""
    config_dict = ctx.obj["CONFIG_DICT"]
    if processor == "collector":
        collect(access_tokens, repo_name, config_dict['query']["body"])
    elif processor == "counter":
        count()
    elif processor == "cleaner":
        clean()

    print("[debug] everything is ok")


# @hydra.main(version_base=None, config_path="./config", config_name="config")
# def collect(cfg: DictConfig):
#     collector = Collector(cfg['access_token'], repos_name=cfg['repos_name'], query=cfg['query']['body'])
#     collector.get_whole_issues(cfg['collect']['to_file'])
#
#
# @hydra.main(version_base=None, config_path="./config", config_name="config")
# def count(cfg: DictConfig):
#     counter = Counter(cfg['count']['from_file'])
#     df = counter.prio_rank({"Comments": 1}, 1000)
#
#     df.to_csv("./results/mindspore_filter_rank.csv")
#
#
# @hydra.main(version_base=None, config_path="./config", config_name="config")
# def clean(cfg: DictConfig):
#     cleaner = Cleaner(cfg['clean']['from_file'])
#     cleaner.clear(cfg['clean']['to_file'])
#     print('finsh')


if __name__ == '__main__':
    cli()
