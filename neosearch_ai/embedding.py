import sys

sys.path.append(".")
sys.path.append("..")

# custom modules
from engine.embeddings import EmbeddingDeployment

# Deploy the Ray Serve application.
embedding_deployment = EmbeddingDeployment.bind()
