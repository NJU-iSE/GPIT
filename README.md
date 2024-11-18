# GHIT (GitHub Issue Tools): A toolkit for GitHub Issues

## Instructions
> [!IMPORTANT]
> 
> You should have GitHub [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) because we use [graphql](https://docs.github.com/en/graphql) to crawl the issues.

> [!WARNING]
> 1. Make sure you have a good network connection to GitHub
> 2. If you want to use LLM analyzer locally, make sure run the code in Linux (because we use [vLLM](https://github.com/vllm-project/vllm) to deploy LLMs)

> [!Note] 
> Before you start, clone the repo plz
> ```bash
> git clone https://github.com/NJU-iSE/GHIT.git
> ```
> then pip install the dependencies:
> ```bash
> pip install -r requirements.txt
>```
#### Quick Start
```bash
# collect the github issues from one specific repo
python main.py --config config/config.yaml data --processor collector --access_tokens ${ACCESS_TOKEN} --repo_name pytorch/pytorch
```
above command can collect all the issues from the repo `pytorch/pytorch`.  
Of course, you can collect issues from other repositories.  
plz change the `${ACCESS_TOKEN}` to your own access tokens  
the results would be saved in `Results/{repo_name}/all_issues.csv`  
```bash
# filter the issues by the given conditions (cleaner)
python main.py --config config/config.yaml data --processor cleaner --repo_name pytorch/pytorch
```
the filter results would be saved in `Results/{repo_name}/cleaned_issues.csv`  
you can change the filter conditions in the code (so sry that this is a dirty operation)

```bash
# count the issues by the given conditions (counter)
python main.py --config config/config.yaml data --processor counter --repo_name pytorch/pytorch
```

> [!IMPORTANT]
> 
> After collecting the above issues, you can use the `analyzer` module (LLM-based) to analyze the issues.

> [!WARNING]
> 
> Due to the analyzer is LLM-based, you may need enough GPU resources to run the analyzer
> (Based on my experience, it needs at least 32GB GPU memory because we use [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)).

```bash
python main.py --config config/config.yaml --repo_name pytorch/pytorch analyze
```

After this step, you would get the results in `Results/{repo_name}/analyzer_results.csv`.  
You can use LLMs to specifically analyze the issues.

## TODO List
- [x] the config file needs to be refined
- [x] Implement basic tools
- [x] use LLM to analyze the issues


## Project structure (ghit)
* processors (the module crawling/cleaning/counting data information from GitHub Issues)
  * tools
* analyzer
  * LDA
  * LLM
* utils


#### Future
- [x] implement LLM analyzer
- [ ] test the System