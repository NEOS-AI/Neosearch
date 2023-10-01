#
# Reference: <https://www.sbert.net/docs/pretrained-models/ce-msmarco.html>
#

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)
import torch


model = AutoModelForSequenceClassification.from_pretrained('model_name')
tokenizer = AutoTokenizer.from_pretrained('model_name')

features = tokenizer(
    ['Query', 'Query'],
    ['Paragraph1', 'Paragraph2'],
    padding=True,
    truncation=True,
    return_tensors="pt"
)

model.eval()
with torch.no_grad():
    scores = model(**features).logits
    print(scores)
