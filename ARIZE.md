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

Possible solution: sample batches of N questions, and see if the results are comparable with the enture set.  If this is
comparable we can use a sample for re-runs.

Here's a run with a sample size of 100:

```text
File: 2025-01_qa_pairs.json
rank: 0, count: 77, percent: 77.0
rank: 1, count: 10, percent: 10.0
rank: 2, count: 2, percent: 2.0
rank: 5, count: 11, percent: 11.0
```
