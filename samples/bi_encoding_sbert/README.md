# Sentence Embeddings for Information Retrieval

Semantic search seeks to improve search accuracy by understanding the content of the search query.
In contrast to traditional search engines which only find documents based on lexical matches, semantic search can also find synonyms.

## Bi Encoder

Bi-Encoders produce for a given sentence a sentence embedding.
We pass to a BERT independently the sentences A and B, which result in the sentence embeddings u and v.
These sentence embedding can then be compared using cosine similarity.

## Cross Encoder

For a Cross-Encoder, we pass both sentences simultaneously to the Transformer network.
It produces than an output value between 0 and 1 indicating the similarity of the input sentence pair.

## References

- [Cross Encoder vs Bi Encoder](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- [Compute Sentence Embeddings](https://www.sbert.net/examples/applications/computing-embeddings/README.html)
- [Retrieve Rerank](https://www.sbert.net/examples/applications/retrieve_rerank/README.html)
- [MS Marco Cross Encoder](https://www.sbert.net/docs/pretrained-models/ce-msmarco.html)
- [SBERT: Sementric Search](https://www.sbert.net/examples/applications/semantic-search/README.html)
