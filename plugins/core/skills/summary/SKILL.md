---
name: summary
description: Summarize the conversation and save it to a markdown file.
disable-model-invocation: true
argument-hint: "[file.md]"
---

Summarize the current conversation and save the result to a file.

## Target file

- If the user provided an argument (`$ARGUMENTS`), use it as the file path.
- If the argument is missing or empty, ask for the output file path using AskUserQuestion.

## Summary format

- Write the summary in the same language as the conversation.
- Use concise bullet points: what was discussed, what decisions were made, what changed.
- If code changes were made, list the main affected files.
- Keep the summary proportional to the conversation length.

## Procedure

1. Determine the target file (from argument or by asking).
2. If the file already exists, ask the user whether to overwrite it.
3. Write a Markdown summary.
4. Save the summary to the file using Write.
5. Confirm to the user where the summary was saved.
