import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import defaultdict


# Initialize the lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


# Function to preprocess and tokenize the text
def preprocess_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and lemmatize the words
    preprocessed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in stop_words]
    
    return preprocessed_tokens


# Function to build the index
def build_index(documents):
    index = defaultdict(list)
    
    for doc_id, document in enumerate(documents):
        tokens = preprocess_text(document)
        
        for token in tokens:
            index[token].append(doc_id)
    
    return index

# Example documents
documents = [
    "This is the first document",
    "This document is the second document",
    "And this is the third one",
    "Is this the first document?"
]

# Build the index
index = build_index(documents)

# Print the index
for token, doc_ids in index.items():
    print(f"{token}: {doc_ids}")
