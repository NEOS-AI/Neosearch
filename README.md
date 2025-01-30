<img src="./assets/neosearch.png" width="200px" height="200px" title="Neosearch_LOGO"/>

# Neosearch

AI-based search engine done right.

Chatbot will understand your query and provide you suitable results by using various tools (code generation, weather search, etc).
![Chat view](./assets/imgs/chat_view.png)

You could maximize or run the generated code in the code view.
![Code view](./assets/imgs/code_view.png)

Also, we support aisearch, which uses external search engines to provide you with the best results.
![Aisearch view](./assets/imgs/search_view.png)

## ToDo

- [ ] Finish implementing AISearch view
    - [ ] Make AISearch view to support tavily
    - [ ] Make AISearch view to support searxng
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
    - [ ] Implement dispatcher for Wikipedia
    - [ ] Implement dispatcher for namuwiki
- [ ] Implement the Hybrid Search retriever
    - [ ] Implement the ParadeDB retriever with LlamaIndex
    - [ ] Add support for caching layer for the retriever
- [x] Update Rag Retriever to use the searxng engine
- [x] Implement the CRAG workflow for the Rag Retriever
    - [x] Add support for CRAG API that runs the CRAG workflow with user's query
- [x] Implement the reranker
    - [x] Add support for Cohere Reranker
    - [x] Add support for [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) Reranker
- [ ] Add support for [late-chunking](https://github.com/jina-ai/late-chunking) for better IR
