import csv

# CSVファイルを読み込む
input_file = 'responses.csv' # 入力ファイル名
output_file = 'BCwords.csv' # 出力ファイル名

with open(input_file, mode='r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    data = set()  # 重複を許さないセットを使用

    for row in reader:
        data.add(tuple(row))  # 各行をタプルとしてセットに追加

# 重複を削除したデータを新しいCSVファイルに書き出す
with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    for row in data:
        writer.writerow(row)
