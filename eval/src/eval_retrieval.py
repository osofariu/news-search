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
    eval_qa_dir = os.path.join(os.path.dirname(__file__), "..", "qa_pairs")
    index_dir = os.path.join(os.path.dirname(__file__), "../..", "index")
    index = Index(max_index_age_days=5, index_path=index_dir)

    eval_scored_qa_dir = os.path.join(
        os.path.dirname(__file__), "..", "qa_pairs_scored"
    )
    os.makedirs(eval_scored_qa_dir, exist_ok=True)
    for eval_qa_file in os.listdir(eval_qa_dir):
        eval_qa_file_path = os.path.join(eval_qa_dir, eval_qa_file)
        scored_eval_qa_file_path = os.path.join(eval_scored_qa_dir, eval_qa_file)
        with open(eval_qa_file_path, "r") as eval_file:
            with open(scored_eval_qa_file_path, "w") as scored_eval_file:
                print(f"evaluate {eval_qa_file} with sample size {sample_size}")
                archive_date = eval_qa_file.split("_")[0]
                search_ranks = []
                num_lines = sum(1 for _ in eval_file)
                eval_file.seek(0)  # Reset file pointer to the beginning of the file
                for idx, qa_data in enumerate(
                    tqdm.tqdm(
                        read_qa_data_from_file(eval_file, sample_size),
                        total=sample_size or num_lines,
                    )
                ):
                    question = qa_data.get("question", "")
                    context = qa_data.get("context", "")
                    if question and context:
                        create_index_if_not_exist(index, index_dir, archive_date)
                        search_results = index.search_index(archive_date, question)
                        try:
                            search_rank = search_results.index(context)
                        except ValueError:
                            search_rank = index.k  # 1 + max records from index
                        qa_data["search_rank"] = search_rank
                        print(json.dumps(qa_data), file=scored_eval_file)
                        search_ranks.append(search_rank)
            unique_values, counts = np.unique(search_ranks, return_counts=True)
            total_counts = sum(counts)
            for value, count in sorted(zip(unique_values, counts)):
                print(
                    f"rank: {value}, count: {count}, percent: {100 * count / total_counts}"
                )


def create_index_if_not_exist(index, index_dir, archive_date):
    index_file = os.path.join(index_dir, f"{archive_date}.faiss_index", "index.faiss")
    if not os.path.exists(index_file):
        print(f"Index for {archive_date} does not exist. Creating it..")
        index.create_vector_store(archive_date)


def read_qa_data_from_file(file, sample_size):
    res = []
    for eval_record in file:
        qa_data = json.loads(eval_record)
        confidence_level = float(qa_data.get("confidence_level", 0))
        if confidence_level == 1.0:
            res.append(qa_data)
    if sample_size is None:
        return res
    else:
        sample_size_random_indexes = [
            random.randint(0, len(res) - 1) for _ in range(sample_size)
        ]
        return list(map(lambda i: res[i], sample_size_random_indexes))


if __name__ == "__main__":
    main(sample_size=100)
