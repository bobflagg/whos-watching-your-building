# Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Data ingestion | Python, `sodapy` | Pulls from NYC Open Data via the Socrata Open Data API (SODA) |
| Graph database | Neo4j Desktop | Local instance for development; migrate to AuraDB or self-hosted for production |
| Graph querying | Cypher | Native Neo4j query language |
| Embeddings | `sentence-transformers` | Runs locally; no API cost |
| Vector index | Neo4j built-in vector index | Co-located with the graph; no separate service required |
| LLM reasoning | Claude via Anthropic API | Powers the answer synthesis and query generation |
| Query orchestration | LangChain | Manages retrieval, routing, and LLM interaction |
| Agent framework | LangChain DeepAgents | Multi-step reasoning and tool-use across the knowledge graph |
| Web search | Tavily Search API | Supplies up-to-date information to the agent as a LangChain tool |
| Interface | Streamlit | Conversational UI and graph visualization |
