import json
import os
import pandas as pd
from phoenix.evals import OpenAIModel, llm_generate

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
other_folder_path = os.path.join(current_dir, "../..", "src")
sys.path.append(other_folder_path)

from utils import get_current_date_key

generate_questions_template = """\
Context information is below.

---------------------
{text}
---------------------

Given the context information and not prior knowledge.
generate only questions based on the below query.

You are a Researcher who wants to index knowledge using just a few key terms so
that it can be referenced easily by customers. Your task is to extract 2 to 5 key terms \
as one string (call it key_germs) that capture then essence of the context information provided.

 Restrict the questions to the context information provided."

**IMPORTANT:** Respond ONLY with valid JSON. Do NOT wrap your answer in markdown formatting, code blocks, or add any extra text. The JSON object must have exactly two keys: "key_terms" (containing the extracted key terms) and "context" (containing the original context).

"""


def output_parser(response: str, index: int):
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        return {"__error__": str(e)}


def gen_qa_pair_file(filename):
    print(f"Generating qa pairs for: {filename}")
    cache_context_df = pd.read_json(filename)
    cache_context_df = cache_context_df.drop(
        labels=["lead_paragraph", "pub_date"], axis=1
    )
    cache_context_df["text"] = cache_context_df.apply(
        lambda row: f"{row.headline} {row.abstract}", axis=1
    )
    questions_df = llm_generate(
        dataframe=cache_context_df,
        template=generate_questions_template,
        model=OpenAIModel(
            model="gpt-4o-mini",
        ),
        output_parser=output_parser,
        concurrency=20,
    )
    return questions_df


def list_files_by_date_reverse(directory):
    filenames = os.listdir(directory)
    filenames.sort(reverse=True)
    return filenames


def main():
    """
    Loop over the JSON files in the `cache` folder and for each news story generate
    a JSON entry with a set of key terms that an LLM has extracted from the context.

    The context is the same as what is used by the index to perform a query, so querying
    the index using the key terms extracted should find the appropriate context most of
    the time.. and we will use the output from this program to evalute the quality
    of the retriever.
    """
    cache_dir = os.path.join(os.path.dirname(__file__), "../..", "cache")
    current_cache_file = f"{get_current_date_key()}.json"
    cache_files = [
        os.path.join(cache_dir, f)
        for f in list_files_by_date_reverse(cache_dir)
        if f.endswith(".json") and f != current_cache_file
    ]

    eval_qa_dir = os.path.join(os.path.dirname(__file__), "..", "qa_pairs")
    os.makedirs(eval_qa_dir, exist_ok=True)

    for cache_file in cache_files:
        questions_df = gen_qa_pair_file(cache_file)
        output_file = os.path.join(
            eval_qa_dir,
            f"{os.path.basename(cache_file).replace('.json', '')}_qa_pairs.json",
        )
        questions_df.to_json(output_file, orient="records", lines=True)


if __name__ == "__main__":
    main()
