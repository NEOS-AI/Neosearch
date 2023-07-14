import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def process_query(query):
    # Tokenize the query
    tokens = word_tokenize(query.lower())

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    # Return the processed query
    processed_query = " ".join(lemmatized_tokens)
    return processed_query

# Example usage
query = "How to build a semantic search engine?"
processed_query = process_query(query)
print(processed_query)
