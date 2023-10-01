import torch
from transformers import BertTokenizer
from torch.optim import Adam
from torch.utils.data import DataLoader
from tqdm import tqdm

# custom modules
from loss import CosineSimilarityLoss
from model import STSBertModel
from dataloaders import DataSequence, collate_fn, load_train_test_data


def model_train(
    tokenizer,
    dataset,
    epochs,
    learning_rate,
    bs,
    model_name: str = 'bert-base-uncased'
):
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    model = STSBertModel(model_name=model_name)
    model.train()

    criterion = CosineSimilarityLoss()
    optimizer = Adam(model.parameters(), lr=learning_rate)

    train_dataset = DataSequence(dataset, tokenizer)
    train_dataloader = DataLoader(train_dataset, num_workers=4, batch_size=bs, shuffle=True)

    if use_cuda:
        model = model.cuda()
        criterion = criterion.cuda()

    for i in range(epochs):
        for train_data, train_label in tqdm(train_dataloader):
            train_data['input_ids'] = train_data['input_ids'].to(device)
            train_data['attention_mask'] = train_data['attention_mask'].to(device)
            del train_data['token_type_ids']

            train_data = collate_fn(train_data)

            output = [model(feature)['sentence_embedding'] for feature in train_data]

            loss = criterion(output, train_label.to(device))
            total_loss_train += loss.item()

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        print(f'Epochs: {i + 1} | Loss: {total_loss_train / len(dataset): .3f}')

    return model


# Function to predict test data
def predict_sts(texts, trained_model, tokenizer):
    test_input = tokenizer(texts, padding='max_length', max_length = 128, truncation=True, return_tensors="pt")
    test_input['input_ids'] = test_input['input_ids']
    test_input['attention_mask'] = test_input['attention_mask']
    del test_input['token_type_ids']

    test_output = trained_model(test_input)['sentence_embedding']
    sim = torch.nn.functional.cosine_similarity(test_output[0], test_output[1], dim=0).item()

    return sim


def main(model_name: str = 'bert-base-uncased'):
    # Set the tokenizer
    tokenizer = BertTokenizer.from_pretrained(model_name)

    # load dataset
    dataset, _, _, text_cat_test = load_train_test_data()

    EPOCHS = 5
    LEARNING_RATE = 1e-6
    BATCH_SIZE = 8

    # Train the model
    trained_model = model_train(tokenizer, dataset, EPOCHS, LEARNING_RATE, BATCH_SIZE)

    # Set the model to evaluation mode and move to CPU
    trained_model.to('cpu')
    trained_model.eval()

    # Predict test data
    result = predict_sts(text_cat_test[245], trained_model, tokenizer)
    print(result)
    result = predict_sts(text_cat_test[420], trained_model, tokenizer)
    print(result)


if __name__ == '__main__':
    main()
