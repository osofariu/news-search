from dataclasses import dataclass
import json
import os
import random
import sys
from typing import List
import numpy as np
import tqdm

current_dir = os.path.dirname(os.path.abspath(__file__))
other_folder_path = os.path.join(current_dir, "../..", "src")
sys.path.append(other_folder_path)
from index import Index

# None if you don't want to sample
type SampleSize = None | int
type QAPairs = List[(str, str)]


def main(sample_size: SampleSize):
    """
    - loop over the files in the `qa_pairs` folder
        - loop over each line
            - for each term in the comma-separated `key_terms` and context:
                - use the FAISS retriever to get the top matches
                - make sure the FAISS output contains the context we expect
                - apply some penality if the match is lower in the list.. TBD
    """

    eval_qa_dir = os.path.join(os.path.dirname(__file__), "..", "qa_pairs")
    eval_qa_files = os.listdir(eval_qa_dir)
    index_dir = os.path.join(os.path.dirname(__file__), "../..", "index")
    index = Index(max_index_age_days=5, index_path=index_dir)

    for eval_qa_file in eval_qa_files:
        eval_qa_file_path = os.path.join(eval_qa_dir, eval_qa_file)
        with open(eval_qa_file_path, "r") as file:
            archive_date = eval_qa_file.split("_")[0]
            qa_pairs = read_qa_pairs_from_file(file, sample_size)
            scores = []
            num_lines = sum(1 for _ in file)
            file.seek(0)  # Reset file pointer to the beginning of the file
            for question, context in tqdm.tqdm(
                read_qa_pairs_from_file(file, sample_size),
                total=sample_size or num_lines,
            ):
                if question and context:
                    create_index_if_not_exist(index, index_dir, archive_date)
                    results = index.search_index(archive_date, question)
                    try:
                        search_rank = results.index(context)
                    except ValueError:
                        search_rank = index.k  # 1 + max records from index
                    scores.append(search_rank)

            unique_values, counts = np.unique(scores, return_counts=True)
            total_counts = sum(counts)
            print(f"File: {eval_qa_file}")
            for value, count in sorted(zip(unique_values, counts)):
                print(
                    f"rank: {value}, count: {count}, percent: {100 * count / total_counts}"
                )


def create_index_if_not_exist(index, index_dir, archive_date):
    index_file = os.path.join(index_dir, f"{archive_date}.faiss_index", "index.faiss")
    if not os.path.exists(index_file):
        print(f"Index for {archive_date} does not exist. Creating it..")
        index.create_vector_store(archive_date)


def read_qa_pairs_from_file(file, sample_size):
    res = []
    for line in file:
        qa_pair = json.loads(line)
        question = qa_pair.get("question", "")
        context = qa_pair.get("context", "")
        res.append((question, context))
    if sample_size is None:
        return res
    else:
        sample_size_random_indexes = [
            random.randint(0, len(res) - 1) for _ in range(sample_size)
        ]
        return list(map(lambda i: res[i], sample_size_random_indexes))


if __name__ == "__main__":
    sample_size = 100
    main(sample_size=100)
