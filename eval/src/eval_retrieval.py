import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
other_folder_path = os.path.join(current_dir, "../..", "src")
sys.path.append(other_folder_path)
from index import Index


def main():
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
            scores = []
            for line in file:
                qa_pair = json.loads(line)
                key_terms = qa_pair.get("key_terms", "")
                context = qa_pair.get("context", "")
                if key_terms and context:
                    key_terms_list = key_terms.split(", ")
                    for term in key_terms_list:
                        create_index_if_not_exist(index, index_dir, archive_date)
                        results = index.search_index(archive_date, term)
                        try:
                            rank = results.index(context)
                        except ValueError:
                            rank = -1
                        scores.append(rank)
                        print(f"term: {term} rank: {rank}")


def create_index_if_not_exist(index, index_dir, archive_date):
    index_file = os.path.join(index_dir, f"{archive_date}.faiss_index", "index.faiss")
    if not os.path.exists(index_file):
        print(f"Index for {archive_date} does not exist. Creating it..")
        index.create_vector_store(archive_date)


if __name__ == "__main__":
    main()
