# Neosearch AI

Run AI models for RAG search.

## Embeddings

```bash
#
# export environment variables
#

# huggingface sentence transformers model
export MODEL_NAME answerdotai/ModernBERT-large
# device type (cpu, gpu, etc)
export DEVICE cpu
# precision (float32, float16, bfloat16, etc)
export PRECISION float32
# retriever batch size
export RETRIEVER_BATCH_SIZE 8
# reader batch size
export READER_BATCH_SIZE 8
# max batch size
export max_batch_size 8

# if you use gpu, then set the num of gpus (otherwise, torch.cuda.device_count() is used)
export NUM_GPUS 1

#
# run ray serve
#

serve run embedding:embedding_deployment
```

## Reranker

### FlashRerank

```bash
#
# export environment variables
#

# huggingface sentence transformers model
export MODEL_NAME rank_zephyr_7b_v1_full
# device type (cpu, gpu, etc)
export DEVICE cpu
# precision (float32, float16, bfloat16, etc)
export PRECISION float32
# retriever batch size
export RETRIEVER_BATCH_SIZE 8
# reader batch size
export READER_BATCH_SIZE 8
# max batch size
export max_batch_size 8

# if you use gpu, then set the num of gpus (otherwise, torch.cuda.device_count() is used)
export NUM_GPUS 1

#
# run ray serve
#

serve run flashrerank:rerank_deployment
```
