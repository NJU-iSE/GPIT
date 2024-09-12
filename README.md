# GHIT (GitHub Issue Tools): A toolkit for GitHub Issues

## Instructions
> [!IMPORTANT]
> 
> You should have GitHub [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)  

> [!WARNING]
> Make sure you have a good network connection to GitHub

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
# collect the github issues
python .\main.py --config config/config.yaml main --processor collector --access_tokens {access_tokens} --repo_name pytorch/pytorch
```
above command can collect all the issues from the repo `pytorch/pytorch`.  
Of course, you can collect issues from other repositories.
plz change the `{access_tokens}` to your own access tokens



## TODO List
- [ ] the config file needs to be refined
- [x] Implement collector
- [ ] Implement cleaner
- [ ] Implement counter
- [ ] Implement analyzer



## Project structure (ghit)
* collector (the module crawling/cleaning/counting data information from GitHub Issues)
  * tools
* analyzer
  * LDA
  * LLM
* utils


#### Future
- [ ] implement LLM analyzer
- [ ] test the System