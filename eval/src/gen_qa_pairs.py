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

You are a Researcher who wants to index knowledge using a question and the related contest to help us
evaluate how good the Retriever is at finding the right context given each question.

Your task is to generate one short question (call it question) that captures the essence of each context provided. Think
of the question as a title for the context given, so we're just looking at a few words.

 Restrict the questions to the context information provided."
 
 Once you have generated the question, reflect on the degree to which the answer to the question is found in the context.
 Explain why you feel the question is relevant to the context (self_reflection), and provide a confidence level 
 (confidence_level) as a float between 0 and 1 where 0 means no confidence, and 1 means complete confidence.

**IMPORTANT:** Respond ONLY with valid JSON. Do NOT wrap your answer in markdown formatting, code blocks, or add any extra text. 
The JSON object must have exactly the following keys: 
- "question" (the generated question)
- "context" (the original context)
- "self_reflection" (the degree to which the question is relevant for the given context)
- "confidence_level" (how confident you are in the questi)

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
            model="gpt-3.5-turbo",
        ),
        output_parser=output_parser,
        concurrency=5,
    )
    return questions_df


def list_files_by_date_reverse(directory):
    filenames = os.listdir(directory)
    filenames.sort(reverse=True)
    return filenames


def main(max_files_to_process: int):
    """
    Loop over the JSON files in the `cache` folder and for each news story generate
    a JSON entry with a question that an LLM has extracted from the context.

    The context is the same as what is used by the index to perform a query, so querying
    the index using the question should find the appropriate context most of
    the time.. and we will look at the ranking of the context (using index search)
    to evalute the quality of the retriever.
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
    files_processed = 0
    for cache_file in cache_files:
        files_processed += 1
        output_file = os.path.join(
            eval_qa_dir,
            f"{os.path.basename(cache_file).replace('.json', '')}_qa_pairs.json",
        )
        if os.path.exists(output_file):
            continue
        questions_df = gen_qa_pair_file(cache_file)

        questions_df.to_json(output_file, orient="records", lines=True)
        if files_processed >= max_files_to_process:
            break


if __name__ == "__main__":
    main(max_files_to_process=1)
