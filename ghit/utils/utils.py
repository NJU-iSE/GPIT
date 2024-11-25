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
    text = text.replace('na', 'nan')

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


def write_to_file(all_issues, repos_name, writer):
    # FIXME@SHAOYU: how to make the filter condition in config yaml?
    for issue in all_issues:
        # for item in issue:
        #     print(item)
        # print(issue['number'])
        # print("https://github.com/pytorch/pytorch"+f"/issues/{issue['number']}")
        title = issue['title']
        body = issue['body']
        code = "\n".join(re.findall(r'```([\s\S]*?)```', body))

        body = body.replace('"', ' ')  # 消除引号部分
        body = re.sub(r'@\w+', '', body)  # 删除@用户名
        body = re.sub(r'```[\s\S]*?```', ' ', body)  # 删除代码块
        body = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', body)
        title = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', title)
        # body = body.replace('\n', ' ').strip()  # 消除回车符并去除首尾空格
        body = body.replace('`', ' ')
        body = body.replace('"', ' ')
        body = body.replace("'", ' ')
        text_list = body.split()
        # 使用列表推导式来过滤掉包含斜杠字符"/"的子字符串
        text_list = [text for text in text_list if '/' or '\\' not in text]
        # 将过滤后的子字符串重新连接成一个文本
        body = ' '.join(text_list)
        # title = word_only(title, 300)
        # body = word_only(body, 300)
        # body = f'"{body}"'
        created_at = issue['createdAt']
        state = issue['state']
        labels = ", ".join(label['name'] for label in issue['labels']['nodes'])
        reactions_count = issue['reactions']['totalCount']  # 获取点赞数
        comments_count = issue['comments']['totalCount']  # 获取评论数
        repo_url = "https://github.com/" + repos_name
        issue_id = issue['number']
        issue_link = f"{repo_url}/issues/{issue_id}"
        writer.writerow([title, body, code, created_at, labels, state, reactions_count,
                         comments_count, issue_link])  # 写入新的列 "Reactions" 和 "Comments"


def get_response_data(url, query, headers, cursor):
    response = requests.post(url, json={"query": query, "variables": {"cursor": cursor}}, headers=headers)
    assert response.status_code == 200, f"{response}"  # set the assertion
    data = response.json()
    total_issues_count = data["data"]["repository"]["issues"]["totalCount"]
    return data, total_issues_count


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