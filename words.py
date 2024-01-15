
import csv
import os
import threading
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

# Environment variable for OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to call OpenAI API
def call_openai_api(term):
    client = OpenAI(OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[
            {"role": "system", "content": "あなたは優秀な解説アシスタントです。提供された単語について、120文字程度の簡単な解説を書き出してください。"},
            {"role": "user", "content": term},
        ],
    )
    if response.choices[0].message.content is None:
        return ""
    else:
        return response.choices[0].text.strip()

# Function to process a chunk of terms
def process_chunk(chunk, output_file_path, lock):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for term in chunk:
            future = executor.submit(call_openai_api, term)
            futures.append((term, future))

        with open(output_file_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            for term, future in futures:
                explanation = future.result()
                with lock:
                    writer.writerow([term, explanation])

# Worker function for threading
def worker(chunks_queue, output_file_path, lock):
    while not chunks_queue.empty():
        chunk = chunks_queue.get()
        process_chunk(chunk, output_file_path, lock)
        chunks_queue.task_done()

# Paths for input and output CSV files
input_file_path = 'bio.csv'  # Adjust as needed
output_file_path = 'output_terms_with_explanations.csv'

# Initialize the output CSV file with headers
with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Term', 'Explanation'])

# Read terms from the input CSV file
terms = []
with open(input_file_path, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    next(reader, None)  # Skip the header
    for row in reader:
        if row:
            terms.append(row[0])

# Split terms into chunks for parallel processing
chunks = [terms[i:i + 100] for i in range(0, len(terms), 100)]

# Create a thread-safe queue and add all chunks
chunks_queue = Queue()
for chunk in chunks:
    chunks_queue.put(chunk)

# Lock for file writing
lock = threading.Lock()

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor(max_workers=3) as executor:
    for _ in range(3):
        executor.submit(worker, chunks_queue, output_file_path, lock)

# Wait for the queue to be empty
chunks_queue.join()

print("All terms have been processed.")
