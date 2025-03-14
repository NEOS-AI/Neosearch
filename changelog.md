# Changelog

## ~ 2025.03.13

- [x] Implementing AISearch view
    - [x] Make AISearch view to support tavily
    - [x] Make AISearch view to support searxng

- [x] Replace poetry with uv
    - [x] Replace poetry with uv for `neosearch`
    - [x] Replace poetry with uv for `neosearch_ai`
    - [x] Replace poetry with uv for `neosearch_llm`
    - [x] Replace poetry with uv for `neosearch_crawler`

- [x] Implement the batch system for spider
    - [x] Implement the spider with Trafilatura
    - [x] Implement the continuous batching for spider

- [x] Update Rag Retriever to use the searxng engine

- [x] Implement the CRAG workflow for the Rag Retriever
    - [x] Add support for CRAG API that runs the CRAG workflow with user's query

- [x] Implement the reranker
    - [x] Add support for Cohere Reranker
    - [x] Add support for [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) Reranker
