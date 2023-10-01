from sentence_transformers import SentenceTransformer
import pickle
import pandas as pd


def create_embeddings_models(
    model_name:str = 'sentence-transformers/all-mpnet-base-v2'
):
    model = SentenceTransformer(model_name)
    return model


def create_sentence_embeddings(
    model_name: str='sentence-transformers/all-mpnet-base-v2',
    description_file: str='descriptions.csv',
    embeddings_file: str='embeddings.pkl'
):
    model = create_embeddings_models(
        model_name=model_name
    )

    with open(description_file, 'r') as f:
        descriptions = f.readlines()
    descriptions = [d.strip().split(',') for d in descriptions]
    for idx, line in enumerate(descriptions):
        descriptions[idx] = [line[0], ','.join(line[1:])]
    
    df = pd.DataFrame(descriptions, columns=['id', 'description'])
    embeddings = model.encode(
        df['description'].tolist(), show_progress_bar=True
    )
    with open(embeddings_file, 'wb') as f:
        pickle.dump(embeddings, f)

    return model
