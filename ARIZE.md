# Using ARIZE Phoenix

Pull the latest image:

```shell
docker pull arizephoenix/phoenix:latest
```

Run the container:

```shell
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
```

We are using a local docker container to investigate the traces created by
the application.  It's nice to have a local solution that uses resources
we deployed rather than rely on an external system.

## Instrumentation

This seems to add traces very similar to Langsmith, though the nesting looks better with `arizephoenix`

[Langchain example](https://github.com/Arize-ai/openinference/blob/main/python/instrumentation/openinference-instrumentation-langchain/examples/chain_metadata.py)

## Evaluations

### Retrieval

1. generate a set of questions from given context (`gen_qa_pairs.py`)

    * make a list of contexts from the JSON Cache. This has to match the content that gets indexed, so `headline` followed by `abstract`

    * for each context ask an llm to generate a relevant question. Save the question and context info a file

2. evaluate the Retriever using the (question, context) pairs (`eval_retrieval.py`)

    * given the (question, context) pairs generated before, use the index retriever
    to see what it retrieves, and in what order when asked that question.

#### Initial results

Example Outputs:

```text
File: 2025-01_qa_pairs.json
rank: 0, count: 3386, percent: 81.74794785127958
rank: 1, count: 257, percent: 6.204732013520038
rank: 2, count: 86, percent: 2.0762916465475616
rank: 3, count: 46, percent: 1.110574601641719
rank: 4, count: 14, percent: 0.3380009657170449
rank: 5, count: 353, percent: 8.522452921294061
```

One issue is performance: for 4-6k stories it take around 20 minutes, and that's just for one month's worth of stories.

Solution: randomly sample batches of N questions, and see if the results are comparable with the enture set.  If this is
comparable we can use a sample for re-runs.

Here's a run with a sample size of 100:

```text
rank: 0, count: 77, percent: 77.0
rank: 1, count: 10, percent: 10.0
rank: 2, count: 2, percent: 2.0
rank: 5, count: 11, percent: 11.0
```

### Changed the gen_qa_pairs prompt to reflect on the quality of the question

Asked it to reason about how relevant the question was given the context, and introduced a confidence_level.
Maybe because it had to reflect, the confidence level comes out very high: either 0.9 or 1.0.

It appears that this extra self-reflection step did improve the quality of the questions as it relates
to the index we created (using the search_index method): it went up by about 10%.

After changing the prompt to evaluate the quality of the question, we get something like this:

```text
rank: 0, count: 86, percent: 86.0
rank: 1, count: 3, percent: 3.0
rank: 2, count: 1, percent: 1.0
rank: 3, count: 1, percent: 1.0
rank: 5, count: 9, percent: 9.0
```

Need to look closer at the rank 5 questions -- these were not found in any contexts.

Finally, we changing the threshold to 1.0 (perfect match), to use better questions, and we get this output:

```text
rank: 0, count: 90, percent: 90.0
rank: 1, count: 3, percent: 3.0
rank: 3, count: 3, percent: 3.0
rank: 5, count: 4, percent: 4.0
```

There are still 4 questions that were not matched.. should add some logging to see why.

So between asking the LLM to self-reflect on the question generation and picking the questions that it
believes are a perfect match according to the context we are *always* able to retrieve the expected context,
and 90% of the time it's the first answer, while the rest 10% come up as later matches (rank is 5)
