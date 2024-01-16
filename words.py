import csv
import os
import asyncio
from openai import AsyncOpenAI

# OpenAI APIキーの環境変数
api_key = os.getenv("OPENAI_API_KEY")

# Semaphoreの最大値を設定
semaphore = asyncio.Semaphore(30)

async def fetch_definition(client, term):
    async with semaphore:
        response = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0,
            messages=[
                {"role": "system", "content": "あなたは優秀な解説アシスタントです。提供された単語について、120文字程度の簡単な解説を書き出してください。"},
                {"role": "user", "content": term},
            ],
        )
        if response == None:
            return term, "解説が見つかりませんでした。"
        else :
            return term, response.choices[0].message.content
    

async def process_terms(input_csv, output_csv):
    client = AsyncOpenAI()

    with open(input_csv, newline='', encoding='utf-8') as infile, \
         open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        batch = []
        for row in reader:
            task = fetch_definition(client, row[0])
            batch.append(task)

            # バッチサイズが100に達した場合、タスクを実行して結果を書き出す
            if len(batch) == 100:
                definitions = await asyncio.gather(*batch)
                for term, definition in definitions:
                    writer.writerow([term, definition])
                batch = []  # バッチをリセット

        # 残りのタスクがある場合、それらを処理
        if batch:
            definitions = await asyncio.gather(*batch)
            for term, definition in definitions:
                writer.writerow([term, definition])


if __name__ == '__main__':
    input_csv = 'bio.csv'
    output_csv = 'output.csv'
    asyncio.run(process_terms(input_csv, output_csv))
