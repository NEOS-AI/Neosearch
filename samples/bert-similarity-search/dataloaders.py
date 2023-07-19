import torch
from datasets import load_dataset


class DataSequence(torch.utils.data.Dataset):

    def __init__(self, dataset, tokenizer):
        similarity = [i['similarity_score'] for i in dataset]
        self.label = [i/5.0 for i in similarity]
        self.sentence_1 = [i['sentence1'] for i in dataset]
        self.sentence_2 = [i['sentence2'] for i in dataset]
        self.text_cat = [[str(x), str(y)] for x,y in zip(self.sentence_1, self.sentence_2)]
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.text_cat)

    def get_batch_labels(self, idx):
        return torch.tensor(self.label[idx])

    def get_batch_texts(self, idx):
        return self.tokenizer(self.text_cat[idx], padding='max_length', max_length = 128, truncation=True, return_tensors="pt")

    def __getitem__(self, idx):
        batch_texts = self.get_batch_texts(idx)
        batch_y = self.get_batch_labels(idx)

        return batch_texts, batch_y

def collate_fn(texts):
    num_texts = len(texts['input_ids'])
    features = list()
    for i in range(num_texts):
        features.append({'input_ids':texts['input_ids'][i], 'attention_mask':texts['attention_mask'][i]})
    
    return features


def load_train_test_data():
    # Dataset for training
    dataset = load_dataset("stsb_multi_mt", name="en", split="train")
    similarity = [i['similarity_score'] for i in dataset]
    normalized_similarity = [i/5.0 for i in similarity]

    # Dataset for test
    test_dataset = load_dataset("stsb_multi_mt", name="en", split="test")

    # Prepare test data
    sentence_1_test = [i['sentence1'] for i in test_dataset]
    sentence_2_test = [i['sentence2'] for i in test_dataset]
    text_cat_test = [[str(x), str(y)] for x,y in zip(sentence_1_test, sentence_2_test)]

    return dataset, normalized_similarity, test_dataset, text_cat_test
