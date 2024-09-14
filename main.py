from ghit.processors.tools import Collector, Cleaner, Counter
import logging
import pandas as pd
import yaml
import click
from utils import load_config_file
from ghit.analyzer.LLM.models import QwenModel

logging.basicConfig(level=logging.INFO)


def collect(access_token, repo_name, query):
    collector = Collector(access_token, repos_name=repo_name, query=query,
                          to_file=f"Results/{repo_name.split('/')[-1]}/all_issues.csv")
    collector.get_whole_issues()


def clean(repo_name):
    assert f"Results/{repo_name.split('/')[-1]}/all_issues.csv" is not None, "you should collect the issues firstly"
    cleaner = Cleaner(f"Results/{repo_name.split('/')[-1]}/all_issues.csv")
    cleaner.clear(f"Results/{repo_name.split('/')[-1]}/cleaned_issues.csv",
                  years=("2020", "2021", "2022", "2023", "2024"), tags="memory", keywords="bug|Bug")


def count(repo_name):
    assert f"Results/{repo_name.split('/')[-1]}/cleaned_issues.csv" is not None, "you should clean the issues firstly"
    counter = Counter(f"Results/{repo_name.split('/')[-1]}/cleaned_issues.csv")
    df = counter.prio_rank({"Comments": 1}, 1000)
    df.to_csv(f"Results/{repo_name.split('/')[-1]}/ranked_issues.csv")
    print(df.__len__())


@click.group()
@click.option(
    "config_file",
    "--config",
    type=str,
    default=None,
    help="Path to the configure file.",
)
@click.option(
    "repo_name",
    "--repo_name",
    type=str,
    default=None,
    help="the path of the repository"
)
@click.pass_context
def cli(ctx, config_file, repo_name):
    """run the main using a configuration file"""
    if config_file is not None:
        config_dict = load_config_file(config_file)
        ctx.ensure_object(dict)
        ctx.obj["CONFIG_DICT"] = config_dict
        ctx.obj["REPO_NAME"] = repo_name


@cli.command("data")
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
def data_process(ctx, processor, access_tokens):
    """ Run data processing"""
    config_dict = ctx.obj["CONFIG_DICT"]
    repo_name = ctx.obj["REPO_NAME"]
    if processor == "collector":
        collect(access_tokens, repo_name, config_dict['query']["body"])
    elif processor == "cleaner":
        clean(repo_name)
    elif processor == "counter":
        count(repo_name)

    print("[dev] everything is ok")


@cli.command("analyze")
@click.pass_context
def analyze(ctx):
    """Run analyzer"""
    config_dict = ctx.obj["CONFIG_DICT"]
    repo_name = ctx.obj["REPO_NAME"]
    model_config = config_dict["model"]

    issues = pd.read_csv(f"Results/{repo_name.split('/')[-1]}/cleaned_issues.csv")

    model = QwenModel(model_path=model_config["model_path"], temperature=model_config["temperature"],
                      top_p=model_config["top_p"], repetition_penalty=model_config["repetition_penalty"],
                      max_tokens=model_config["max_tokens"])

    analysis_result = []

    for index, issue in issues.iterrows():
        title = issue["Title"]
        body = issue["Body"]
        code = issue["Code"]

        prompt_template = model_config["prompt_template"]
        prompt = prompt_template.format(title=title, body=body, code=code)

        outputs = model.get_answer(system_content=model_config["system_content"], prompt=prompt)

        answer = outputs[0].outputs[0].text
        analysis_result.append(answer)

    issues["Analysis"] = analysis_result

    output_file_path = f"Results/{repo_name.split('/')[-1]}/analyzed_issues.csv"
    issues.to_csv(output_file_path, index=False)

    print(f"[dev] fin!")

if __name__ == '__main__':
    cli()
