# GPIT (*G*itHub *P*ull Request & *I*ssue *T*ools): A toolkit for GitHub Pull Requests and Issues

## ✨️Introduction
GPIT is a simple and easy toolkit for collecting, cleaning, and analyzing GitHub Pull Requests (PRs) and Issues.

> [!WARNING]
> **Precautions**
> - **OS**: Recommend Ubuntu System;
> - **Network**: Good Network to GitHub; 
> - **LLM usage**:If you want to use LLM analyzer locally, make sure run the code in Linux (because we use vLLM to deploy LLMs)


## 🌠Quick Start

> [!Note] 
> Before you start, clone the repo plz
> ```bash
> git clone https://github.com/NJU-iSE/GPIT.git
> cd GPIT
> ```
> 
> You should have GitHub [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) because we use [graphql](https://docs.github.com/en/graphql) to crawl the issues.
> ```bash
>echo [YOUR_GITHUB_PAT] > config/github_pat.txt  # replace [YOUR_GITHUB_PAT] with your GitHub PAT
>```
>
> then pip install the dependencies:
> ```bash
> pip install -r requirements.txt
>```


#### 📩Data collection
```bash
# collect the github issues from one specific repo
python main.py --repo_path pytorh/pytorch run_collection \
              --query_type issue
```
above command can collect all the issues from the repo `pytorch/pytorch`.  
Of course, you can collect issues from other repositories.  
Additionally, you can also collect Pull Requests by using `--query_type PR`.  
the results would be saved in `Results/{repo_name}/all_{query_type}.csv`  

#### 🧹Data cleaning
```bash
# filter the issues by the given conditions (cleaner)
python main.py --repo_path pytorh/pytorch run_cleaning \
              --query_type issue \
              --years [2020,2021,2022,2023,2024] \
              --tags "high priority"  \
              --save_cols [Title,Tags,Link,Year]
```
the filter results would be saved in `Results/{repo_name}/cleaned_issues.csv`  
you can change the filter conditions in the code (so sry that this is a dirty operation)

#### 📊Data statistics
```bash
# count the issues by the given conditions (counter)
python main.py --config config/config.yaml data --processor counter --repo_name pytorch/pytorch
```

#### 🔍️Issue analyzing (stay tuned)
> [!IMPORTANT]
> 
> After collecting the above issues, you can use the `analyzer` module (LLM-based) to analyze the issues. currently, we use local inference engines to deploy systems.

> [!WARNING]
> 
> Due to the analyzer is LLM-based, you may need enough GPU resources to run the analyzer
> (Based on my experience, it needs at least 32GB GPU memory because we use [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)).

```bash
python main.py --config config/config.yaml --repo_name pytorch/pytorch analyze
```

After this step, you would get the results in `Results/{repo_name}/analyzer_results.csv`.  
You can use LLMs to specifically analyze the issues.

## 🛠️TODO List
- [ ] support more LLMs (e.g., deepseek), especially using API service
- [ ] Implement batch processing for `run_collection`
- [ ] use logging tools instead of `print`
- [ ] test the System
- [x] Add support for collecting PRs like issues. 
- [x] the config file needs to be refined
- [x] Implement basic tools
- [x] use LLM to analyze the issues

