import gensim
from gensim.models import Word2Vec

# Load pre-trained word embeddings model
model = gensim.models.KeyedVectors.load_word2vec_format('path_to_word_embeddings.bin', binary=True)

# Define a function to calculate the semantic similarity between two sentences
def calculate_similarity(sentence1, sentence2):
    # Tokenize the sentences into words
    words1 = sentence1.lower().split()
    words2 = sentence2.lower().split()

    # Remove stop words, punctuation, or any other preprocessing steps if needed

    # Calculate the average word embedding for each sentence
    embedding1 = sum(model[word] for word in words1 if word in model) / len(words1)
    embedding2 = sum(model[word] for word in words2 if word in model) / len(words2)

    # Calculate the cosine similarity between the sentence embeddings
    similarity = embedding1.dot(embedding2) / (embedding1.norm() * embedding2.norm())

    return similarity

# Example usage
sentence1 = "I want to book a flight from New York to London"
sentence2 = "Can you help me find a flight from NYC to London?"

similarity_score = calculate_similarity(sentence1, sentence2)
print(f"Semantic similarity score: {similarity_score}")
