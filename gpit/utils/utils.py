import re
import nltk
from nltk.corpus import stopwords
import requests
import email
import yaml


nltk.download('stopwords')
nltk_stopwords = set(stopwords.words('english'))

def process_text(text):
    if isinstance(text, float):
        return ''
    # TODO@YSY: put these into parameter control
    # text = text.lower()
    # replace "error" as "bug"
    # text = text.replace('error', 'bug')
    # text = text.replace('na', 'nan')

    # delete the words containing "http"
    text = re.sub(r'http\S+', '', text)

    # delete one word
    text = re.sub(r'\b\w\b', '', text)

    # delete the specific words
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        words_to_remove = [line.strip() for line in f.readlines()]
    # words_pattern = '|'.join([re.escape(word) for word in words_to_remove])
    # words_pattern = r'\b(?:' + words_pattern + r')\b|\w*(' + words_pattern + r')\w*'
    words_pattern = r'\b(?:' + '|'.join(re.escape(word) for word in words_to_remove) + r')\b'

    # use re to match the strings or substring is space
    text = re.sub(words_pattern, ' ', text, flags=re.IGNORECASE)

    text_list = text.split(" ")

    text_list = [x for x in text_list if x][:300]

    # remove the stopwords
    text_list = [word for word in text_list if word not in nltk_stopwords]

    text = " ".join(text_list)

    return text.strip()


def word_only(intput_text: str, numbers: int):
    intput_text = intput_text.replace('.', ' ')
    str_list = intput_text.split(" ")
    str_list = [x for x in str_list if x][:numbers]
    output = " ".join(str_list)
    return output


def write_to_file(all_items, query_type, repos_name, writer):
    # FIXME@SHAOYU: how to make the filter condition in config yaml?
    for item in all_items:
        title = item['title']
        body = item['body']
        code = "\n".join(re.findall(r'```([\s\S]*?)```', body))

        body = body.replace('"', ' ')  # eliminate the "
        body = re.sub(r'@\w+', '', body)  # delete @account
        body = re.sub(r'```[\s\S]*?```', ' ', body)  # delete code block
        body = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', body)
        title = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', title)
        # body = body.replace('\n', ' ').strip()  # eliminate the \n
        body = body.replace('`', ' ')
        body = body.replace('"', ' ')
        body = body.replace("'", ' ')
        text_list = body.split()
        text_list = [text for text in text_list if '/' or '\\' not in text]
        body = ' '.join(text_list)
        # title = word_only(title, 300)
        # body = word_only(body, 300)
        # body = f'"{body}"'
        created_at = item['createdAt']
        state = item['state']
        labels = ", ".join(label['name'] for label in item['labels']['nodes'])
        reactions_count = item['reactions']['totalCount']  # get reactions count
        comments_count = item['comments']['totalCount']  # get comments count
        repo_url = "https://github.com/" + repos_name
        item_id = item['number']
        item_type = "issues" if query_type=="issue" else "pull"
        item_link = f"{repo_url}/{item_type}/{item_id}"
        writer.writerow([title, body, code, created_at, labels, state, reactions_count,
                         comments_count, item_link])  # write reactions and comments count to file


def get_response_data(url, query, response_type, headers, variables=None):
    response_type = "issues" if response_type == "issue" else "pullRequests"
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    assert response.status_code == 200, f"{response}"  # set the assertion
    data = response.json()
    total_items_count = data["data"]["repository"][f"{response_type}"]["totalCount"]
    return data, total_items_count


def draw_line_chart(title, x_label, y_label, x_data, y_data, save_path=None):
    import matplotlib.pyplot as plt
    plt.plot(x_data, y_data)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if save_path:
        plt.savefig(save_path)
    plt.show()
    return

def load_config_file(filepath: str):
    """Loads a YAML configuration file."""
    with open(filepath, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config