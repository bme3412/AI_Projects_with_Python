import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure you have the necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

# Read text from PDF
transcript = extract_text_from_pdf("/Users/brendan/Desktop - Brendan’s MacBook Air/llm/langchain/NFLX_Q3_2023.pdf")

def extract_keywords(transcript):
    # Tokenize the transcript
    tokens = word_tokenize(transcript)

    # Remove stopwords and lower the tokens
    tokens = [word.lower() for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stopwords.words('english')]

    # Join the tokens back into a string
    processed_transcript = ' '.join(tokens)

    # Apply TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_transcript])

    # Extract the scores and feature names
    feature_array = vectorizer.get_feature_names_out()
    tfidf_sorting = tfidf_matrix.toarray().flatten().argsort()[::-1]

    # Select top n features/words
    n = 10  # number of top features/words to extract
    top_n_words = [feature_array[i] for i in tfidf_sorting[:n]]

    return top_n_words

# Example usage

keywords = extract_keywords(transcript)
print(keywords)