# Phase 0 — Foundation: Plan

## Group 1 — Project Dependencies

1. Identify all packages needed across the full roadmap (sodapy, neo4j, langchain, langchain-community, sentence-transformers, anthropic, tavily-python, python-dotenv, streamlit)
2. Add each as a project dependency via `uv add <package>`
3. Verify `uv.lock` is updated and committed

## Group 2 — Environment Configuration

1. Identify every secret and config value the project will need (NYC Open Data app token, Anthropic API key, Tavily API key, Neo4j URI, Neo4j username, Neo4j password)
2. Create `.env.example` with all keys, placeholder values, and inline comments describing each
3. Confirm `.env` is in `.gitignore` (and not accidentally tracked)
