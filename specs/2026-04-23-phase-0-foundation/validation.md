# Phase 0 — Foundation: Validation

## Done when:

### Dependencies
- [ ] `uv sync` completes with no errors on a clean checkout
- [ ] The following packages import without error in a Python REPL:
  ```python
  import sodapy
  import neo4j
  import langchain
  import sentence_transformers
  import anthropic
  import tavily
  import dotenv
  import streamlit
  ```

### Environment configuration
- [ ] `.env.example` exists at the repo root and contains every key the application reads, with a comment describing each
- [ ] `.env` is listed in `.gitignore` and does not appear in `git status`
- [ ] `git grep -r "API_KEY\|SECRET\|PASSWORD" -- ':(exclude).env.example' ':(exclude)specs/'` returns no matches (no secrets in code)
