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
