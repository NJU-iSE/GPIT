from ghit.processors.tools import Collector, Cleaner, Counter
import logging
import yaml
from jinja2 import Template
import click
from utils import load_config_file

logging.basicConfig(level=logging.INFO)


def collect(access_token, repo_name, query):
    collector = Collector(access_token, repos_name=repo_name, query=query,
                          to_file=f"Results/{repo_name.split('/')[-1]}/all_issues.csv")
    collector.get_whole_issues()


def count(repo_name):
    assert f"Results/{repo_name.split('/')[-1]}/all_issues.csv" is not None, "you should collect the issues firstly"
    counter = Counter(f"Results/{repo_name.split('/')[-1]}/all_issues.csv")
    df = counter.prio_rank({"Comments": 1}, 1000)

    df.to_csv(f"Results/{repo_name.split('/')[-1]}/ranked_issues.csv")


def clean(repo_name):
    cleaner = Cleaner(f"Results/{repo_name.split('/')[-1]}/all_issues.csv")
    cleaner.clear(f"Results/{repo_name.split('/')[-1]}/cleaned_issues.csv", years=("2020", "2021", "2022", "2023", "2024"), tags="memory", keywords="bug|Bug")



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
    help="use the specific processor to do something (i.e., processors, counter, and cleaner)"
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
        count(repo_name)
    elif processor == "cleaner":
        clean(repo_name)

    print("[dev] everything is ok")


if __name__ == '__main__':
    cli()
