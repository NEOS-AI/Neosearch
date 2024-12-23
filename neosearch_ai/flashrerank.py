import sys

sys.path.append("..")

# custom modules
from engine.flash_reranker import FlashRerankDeployment

# Deploy the Ray Serve application.
rerank_deployment = FlashRerankDeployment.bind()
