python main.py --repo_path sgl-project/sglang run_collection \
--query_type PR \

python main.py --repo_path sgl-project/sglang run_cleaning \
--query_type PR \
--body_keywords "Fix|fix" \
--save_cols "[Title, Tags, State, Link]"