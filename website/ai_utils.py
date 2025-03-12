from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    if not text:
        return 0.0
    blob = TextBlob(text)
    return blob.sentiment.polarity

def categorize_customer(email, notes):
    """Simple rule-based customer categorization"""
    text = f"{email} {notes if notes else ''}"
    text = text.lower()
    
    categories = {
        'vip': ['premium', 'vip', 'priority', 'urgent'],
        'business': ['corp', 'business', 'company', 'enterprise'],
        'support': ['help', 'support', 'issue', 'problem'],
        'sales': ['purchase', 'buy', 'price', 'cost'],
        'general': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'general'

def calculate_priority(sentiment_score, category):
    """Calculate priority score based on sentiment and category"""
    category_weights = {
        'vip': 5,
        'business': 4,
        'support': 3,
        'sales': 2,
        'general': 1
    }
    
    # Convert sentiment from [-1, 1] to [0, 5]
    sentiment_weight = (sentiment_score + 1) * 2.5
    
    # Combine category and sentiment weights
    priority = category_weights.get(category, 1) + sentiment_weight
    return min(int(priority), 10)  # Scale to 1-10

def smart_search(query, records, fields=['first_name', 'last_name', 'email', 'notes']):
    """Search records using TF-IDF and cosine similarity"""
    if not records:
        return []
    
    # Combine specified fields into documents
    documents = []
    for record in records:
        doc = ' '.join(str(getattr(record, field, '')) for field in fields)
        documents.append(doc)
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([query] + documents)
    
    # Calculate similarities
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    
    # Get sorted indices of most similar records
    similar_indices = np.argsort(similarities)[::-1]
    
    # Return records sorted by similarity, only if similarity > 0
    return [(records[i], similarities[i]) for i in similar_indices if similarities[i] > 0]
