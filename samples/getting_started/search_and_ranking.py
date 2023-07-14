import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize NLTK modules
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Preprocess the documents
def preprocess_documents(documents):
    # Tokenize the documents
    tokenized_documents = [word_tokenize(doc.lower()) for doc in documents]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_documents = [[word for word in doc if word not in stop_words] for doc in tokenized_documents]
    
    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    lemmatized_documents = [[lemmatizer.lemmatize(word) for word in doc] for doc in filtered_documents]
    
    # Convert the documents back to string
    preprocessed_documents = [' '.join(doc) for doc in lemmatized_documents]
    
    return preprocessed_documents

# Perform semantic search
def semantic_search(query, documents):
    # Preprocess the query
    preprocessed_query = preprocess_documents([query])[0]
    
    # Preprocess the documents
    preprocessed_documents = preprocess_documents(documents)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform the preprocessed documents
    tfidf_matrix = vectorizer.fit_transform(preprocessed_documents)
    
    # Transform the preprocessed query
    query_vector = vectorizer.transform([preprocessed_query])
    
    # Calculate cosine similarity between query and documents
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
    
    # Sort the documents by similarity score
    sorted_indices = similarity_scores.argsort()[0][::-1]
    
    # Return the sorted documents
    sorted_documents = [documents[i] for i in sorted_indices]
    
    return sorted_documents

# Example usage
documents = [
    "This is the first document",
    "This document is the second document",
    "And this is the third one",
    "Is this the first document?"
]
query = "This is the first document"

results = semantic_search(query, documents)
print(results)
