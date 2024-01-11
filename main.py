from openai import OpenAI
import os
import csv
import json
# OpenAI APIのキーを環境変数から取得
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']


def read_and_split_file(file_path, chunk_size=5000):
    """
    指定されたファイルを読み込み、指定されたサイズで分割する関数。
    :param file_path: 読み込むファイルのパス。
    :param chunk_size: 分割する文字数。
    :return: 分割されたテキストのリスト。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # テキストを指定されたサイズで分割
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

system_prompt = """
あなたは最先端技術の用語集を作成するアシスタントです。与えられた文章の内容から、3Dプリンター、AI（人工知能）、IoT、VR/AR、エッジコンピューティング、エネルギー技術、サイバーセキュリティ、スペーステクノロジー、ドローン、ニューロテクノロジー、バイオテクノロジー、ビッグデータ、ブロックチェーン、ヘルスケアテクノロジー、メタバース、量子コンピューターに関する用語を出来る限り多く抜き出してJSON形式でパースしてください。
用語に関しては、基礎的な用語から専門的な用語まで、幅広く抜き出してください。また、それらに関連しているであろう固有名詞もできる限り多く抜き出してください。関係ない用語が多少出てきても構いませんのでできる限り多くの用語を抜き出してください。
JSONのキーはwordsとし、値は用語の配列としてください。用語は重複しないようにしてください。
"""

def call_openai_api(content):
    client = OpenAI(OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"}
    )
    if response.choices[0].message.content is None:
        return {}
    else:
        return json.loads(response.choices[0].message.content)

# ファイルパスの指定（例: 'example.txt'）
file_path = 'example.txt'

# ファイルを読み込み、5000文字ごとに分割
chunks = read_and_split_file(file_path)

# 応答を格納するリスト
responses = []
# 他の応答を格納するリスト
other_responses = []

# 各チャンクに対してAPIを呼び出し
for chunk in chunks:
    response = call_openai_api(chunk)
    if response != {}:
        # 'words' キーの内容を処理
        if 'words' in response:
            responses.extend(response['words'])

        # 'words' 以外のキーの内容を処理
        for key, value in response.items():
            if key != 'words':
                other_responses.append({key: value})

# CSVファイルに応答を保存
with open('responses.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Response'])
    for response in responses:
        writer.writerow([response])

# 別のCSVファイルに他の応答を保存
with open('other_responses.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Key', 'Value'])
    for response in other_responses:
        for key, value in response.items():
            writer.writerow([key, value])