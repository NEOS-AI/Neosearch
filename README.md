# Neosearch

AI-based search engine done right.

## ToDo

- [x] Compare trafilatura bs4 and newspaper3k
- [ ] Implement the bulk indexer
- [ ] Implement the batch system for spider
    - [ ] Implement the spider with Trafilatura
        - [ ] Parse title, body, and metadata from HTML
        - [ ] Parse title, body, and metadata from PDF, etc
- [ ] Implement the dispatcher
    - [x] Implement dispatcher for linkedin
    - [x] Implement dispatcher for GitHub
    - [x] Implement dispatcher for Medium
    - [ ] Implement dispatcher for X (previously Twitter)
- [ ] Implement the ParadeDB retriever with LlamaIndex
- [ ] Update Rag Retriever to use the searxng engine
- [ ] Implement the reranker
    - [ ] Add support for Cohere Reranker
    - [x] Add support for [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) Reranker
- [ ] Add support for [late-chunking](https://github.com/jina-ai/late-chunking) for better IR
