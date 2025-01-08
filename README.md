# News Search

## MVP
- take user input in natural language,  containing:
  - topic (a list of words)
  - a date range (TBD, but start simple)
- search NTY archive for articles related to the topic

## Steps 

Some are parallel some are not:

### 1. parse natural language to extract topic and date range
    - in: text
    - out: 
    ```
      {
        topic,
        start_date,
        end_date:
      }
      ```

    - create some tests that evaluate some typical inputs, to make sure it does well enough
    - determine how to handle errors -- such as when it can't extract key info to call the function.
    - (maybe later) may ask an LLM to judge whether the results extracted are sufficient to deduce whether
      those fields were extracted correctly and return a confidence score

### 2.  search New York times Archive to get summary and url by date range
    - input: from 1.topic
    - output:
```
      [{
        - pub_date,
        - archive,
        - snippet,
        - web_url,
        - TBD
      }]
```
  - need a start / end year and month (can assume 1 if not present)
  - download the date with multiple calls (add caching later so we don't get duplicates)

### 3.  use the search results to find interesting articles (filter)
  - input: 1.topic, 2.output (array)
  - output: same as 2.output

### 4.  given list of article from above, find stories related to the user topic
  - input: 1.topic, 2.output (array)
  - output: 2.output (array), having been filtered by topic, confidence score for each match

### 5.  for each match: prompt user for interest
  - input: 4.output
  - output: keep ? download content : END

### 6.  for each interest: download the article (TBD how) and save it
  - input: URL
  - output: HTML content of the article

### 7.  for each article saved: ask an LLM for a summary
  - input: list of article details 
  - output: list of summaries for input details

## NYT Archive API notes

Sample queries to experiment with the API:

Download archives:

``` sh a
curl -s -o nyt-2024-1.json https://api.nytimes.com/svc/archive/v1/2024/1.json\?api-key\=<NYT_API_KEY>
```

Extract key info:
```
cat nyt-2024-1.json | jq '.response.docs ' | jq 'map({abstract,web_url,snippet,lead_paragraph})'
```