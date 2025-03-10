<img src="./assets/neosearch.png" width="200px" height="200px" title="Neosearch_LOGO"/>

# Neosearch

AI-based search engine done right.

Chatbot will understand your query and provide you suitable results by using various tools (code generation, weather search, etc).
![Chat view](./assets/imgs/chat_view.png)

## Features

You could maximize or run the generated code in the code view.
![Code view](./assets/imgs/code_view.png)

Also, we support aisearch, which uses external search engines to provide you with the best results.
![Aisearch view](./assets/imgs/search_view.png)

Neosearch supports real-time search with citation.
![AI search with citation](./assets/imgs/aisearch_result.png)

The LLM chatbot suggests the next question candidates for the user.
![Next question candidates](./assets/imgs/aisearch_question_suggestion.png)

## ToDo

- [x] Implementing AISearch view
    - [x] Make AISearch view to support tavily
    - [x] Make AISearch view to support searxng
- [x] Add support for reasoning model in the chatbot view
- [ ] Add support for Deep Research
    - [ ] Make the result of the Deep Research to be downloadable as PDF or something else
- [x] Compare trafilatura bs4 and newspaper3k
- [x] Replace poetry with uv
    - [x] Replace poetry with uv for `neosearch`
    - [x] Replace poetry with uv for `neosearch_ai`
    - [x] Replace poetry with uv for `neosearch_llm`
    - [x] Replace poetry with uv for `neosearch_crawler`
- [ ] Implement the bulk indexer
- [x] Implement the batch system for spider
    - [x] Implement the spider with Trafilatura
    - [x] Implement the continuous batching for spider
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
- [ ] Add Near-deduplication feature for the crawler/indexer
- [ ] Add support for [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai)
