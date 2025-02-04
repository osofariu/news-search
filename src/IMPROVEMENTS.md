# Things to do at some point (but not now)

## Evaluations

Changing the prompt can address an issue but cause other issues. I need a systematic way of evaluating changes.

Ideally I have some mechanism of evaluating the graph with different inputs, and can handle multi-turn prompts
as part of the evaluation, so I can evaluate how the graph responds.  So I need to:

- expect model to prompt me for input in some cases, and have the ability to give it that
- expect model to **not** prompt me for input in other cases, and penalize it if it does ask questions
- expect model to use the tool correctly give the conversation history

This was just for one tool.  Once I add more tools I can add more criteria to the evaluation.

## Prompt improvements

Asked ChatGPT, and these seem like good suggestions.

### From gpt4o in Cursor - comments

Your prompt seems to generally convey the task clearly, but expanding on a few points and clarifying some areas could improve its effectiveness. Here are some suggestions, along with questions that could help refine it further:

Clarify the Purpose and Tool Usage:

Current State: The prompt notes the use of the nyt_archive_search tool but doesn't specify how to interpret or use its results.
Enhancement: Provide a brief explanation of how to utilize the returned list of articles. For example, are there specific criteria for what makes an article "interesting" or relevant to the user's interests?
Clarify the Input:

Questions:
How will the user's topic of interest be inputted or determined? Does the user explicitly state it, or should the script infer it from context?
What should be done if the user does not provide a date range? Should they be prompted, and how should we phrase such a prompt?
Enhance Error Handling:

Current State: You mention asking for clarification if the topic, start date, and end date cannot be determined.
Enhancement: Define a structured way to request this clarification. For instance, is there a specific order or format for these questions?
Questions:
What should the script do if the user provides invalid date ranges, like those exceeding today's date?
General Improvements:

Enhancement: Add more example date ranges to cover edge cases, such as "next year" or "in the past decade."
Questions:
Would it be helpful to include examples of both well-constructed inquiries and common pitfalls or ambiguous queries?
How should the script handle requests if the today's date passed in might be different from the system's current date (for future-proofing)?
By addressing these points and refining based on the answers to these questions, you can improve clarity, functional robustness, and user guidance in your prompt.

### Actual suggestions

```python
SYSTEM_MESSAGE = f"""
You are a **helpful librarian** who assists users in searching the **New York Times Archive** for news articles based on a **topic** and a **date range**.

**Your Task:**
- Determine the **topic** the user is interested in.
- Identify the **start date** and **end date** for the search.
- Ensure the **start date is after 1852** and the **end date is no later than today**.
- If any required information is missing, **ask the user for clarification**.

**Today's Date:** {today}

---

### **Handling Date Ranges**
Here’s how to interpret common date expressions:

- **"from September 2024 through the end of the year"** → `start_date = "2024-09"`, `end_date = "2024-12"`
- **"from 2020 through 2021"** → `start_date = "2020-01"`, `end_date = "2021-12"`
- **"from September 2025 through today"** → `start_date = "2025-09"`, `end_date = "{today_short}"`
- **"since December 2024"** → `start_date = "2024-12"`, `end_date = "{today_short}"`
- **"this year to date"** → `start_date = "{year}-01"`, `end_date = "{today_short}"`
```
