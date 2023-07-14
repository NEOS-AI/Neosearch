from sklearn.feature_extraction.text import TfidfVectorizer

# Sample documents
documents = [
    "This is the first document.",
    "This document is the second document.",
    "And this is the third one.",
    "Is this the first document?",
]

# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Fit and transform the documents
features = vectorizer.fit_transform(documents)

# Print the feature names
print("Feature names:", vectorizer.get_feature_names())

# Print the feature matrix
print("Feature matrix:")
print(features.toarray())
