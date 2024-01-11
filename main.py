from openai import OpenAI
import os
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# OpenAI APIのキーを環境変数から取得
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

def read_and_split_file(file_path, chunk_size=10000):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

system_prompt = """
あなたは最先端技術の用語集を作成するアシスタントです。与えられた文章の内容から、3Dプリンター、AI（人工知能）、エネルギー技術、サイバーセキュリティ、ニューロテクノロジー、バイオテクノロジー、ビッグデータ、ブロックチェーン、ヘルスケアテクノロジーに関する用語を出来る限り多く抜き出してJSON形式でパースしてください。
用語に関しては、基礎的な用語から専門的な用語まで、幅広く抜き出してください。また、それらに関連しているであろう固有名詞もできる限り多く抜き出してください。関係ない用語が多少出てきても構いませんのでできる限り多くの用語を抜き出してください。
JSONのキーはwordsとし、値は用語の配列としてください。用語は重複しないようにしてください。
"""

def call_openai_api(content):
    client = OpenAI()
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

# CSVファイルへの書き込み用ロック
responses_lock = Lock()
other_responses_lock = Lock()

def process_chunk(chunk, responses_writer, other_responses_writer):
    response = call_openai_api(chunk)
    if response != {}:
        # 'words' キーの内容を処理
        if 'words' in response:
            with responses_lock:
                for word in set(response['words']):  # 重複除去
                    responses_writer.writerow([word])

        # 'words' 以外のキーの内容を処理
        with other_responses_lock:
            for key, value in response.items():
                if key != 'words':
                    other_responses_writer.writerow([key, value])

# メイン処理
file_path = 'ブロックチェーン.txt'
chunks = read_and_split_file(file_path)

with open('responses.csv', 'w', newline='', encoding='utf-8') as responses_file, \
     open('other_responses.csv', 'w', newline='', encoding='utf-8') as other_responses_file:
    
    responses_writer = csv.writer(responses_file)
    other_responses_writer = csv.writer(other_responses_file)

    responses_writer.writerow(['Response'])
    other_responses_writer.writerow(['Key', 'Value'])

    # ThreadPoolExecutorを使用してチャンクを並列処理
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_chunk, chunk, responses_writer, other_responses_writer) for chunk in chunks]
        for future in as_completed(futures):
            future.result()  # 例外が発生した場合にキャッチするためにresultを呼び出す
