import nltk
from nltk.corpus import stopwords
import string
from collections import Counter

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def preprocess_and_count(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    words = [w for w in words if w.isalpha() and w not in stop_words]
    return Counter(words)