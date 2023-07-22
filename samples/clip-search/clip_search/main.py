import faiss
import pickle
import gradio as gr

# custom modules
from instruct_blip import create_descriptions
from sentence_embeddings import create_sentence_embeddings


def clusterize_embeddings(
    embeddings_file: str='embeddings.pkl',
    n_clusters: int=5,
):
    with open(embeddings_file, 'rb') as f:
        embeddings = pickle.load(f)
    embeddings = embeddings.astype('float32')
    embedding_size = embeddings.shape[1]

    quantizer = faiss.IndexFlatIP(embedding_size)
    index = faiss.IndexIVFFlat(
        quantizer, embedding_size, n_clusters, faiss.METRIC_INNER_PRODUCT
    )
    index.train(embeddings)
    index.add(embeddings)

    return index

def search(
    model,
    index,
    query,
    num_results:int = 5,
):
    query_embedding = model.encode(
        query
    )
    query_embedding = query_embedding.numpy().astype('float32')
    query_embedding = query_embedding.reshape(1, -1)

    D, I = index.search(query_embedding, num_results)
    return D, I


#--- main ---

create_descriptions(
    img_dir='instruct_blip_images',
)
model = create_sentence_embeddings(
    model_name='sentence-transformers/all-mpnet-base-v2',
    description_file='descriptions.csv',
    embeddings_file='embeddings.pkl'
)
index = clusterize_embeddings()


def _search():
    _, I = search(
        model,
        index,
        'a dog with a red collar',
        num_results=5,
    )
    images = [f'instruct_blip_images/{i}.jpg' for i in I[0]]
    return images


if __name__ == '__main__':
    with gr.Blocks() as block:
        block.query = gr.inputs.Textbox(
            lines=1, placeholder='Enter a description...'
        )
        outputs = gr.Gallery(
            preview=True
        )
        submit = gr.Button(
            _search,
            text='Search',
            outputs=outputs,
        )
