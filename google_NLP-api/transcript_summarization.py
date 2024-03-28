import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def textrank_summarization(transcript, num_sentences=3):
    sentences = sent_tokenize(transcript)
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))

    def preprocess(sentence):
        words = word_tokenize(sentence.lower())
        words = [stemmer.stem(word) for word in words if word not in stop_words]
        return " ".join(words)

    preprocessed_sentences = [preprocess(sentence) for sentence in sentences]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_sentences)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    scores = nltk.pagerank(similarity_matrix)
    ranked_sentences = sorted(((scores[i], sentence) for i, sentence in enumerate(sentences)), reverse=True)

    summary_sentences = [sentence for _, sentence in ranked_sentences[:num_sentences]]
    summary = " ".join(summary_sentences)

    return summary

# Load the JSON file
with open("GOOGL_Q4_2023.json", "r") as file:
    data = json.load(file)

# Extract the transcript content from the JSON data
transcript = data["content"]

# Generate a summary using TextRank
summary = textrank_summarization(transcript)
print("Summary:")
print(summary)