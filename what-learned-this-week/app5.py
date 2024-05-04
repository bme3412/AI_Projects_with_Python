from flask import Flask, render_template, request
import glob
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
nltk.download('punkt')

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

        # Extract directly from the dictionary
        content = data.get('content', '')
        symbol = data.get('symbol', '')
        year = data.get('year', '')
        quarter = data.get('quarter', '')
        date = data.get('date', '')

        return content, symbol, year, quarter, date


def extract_discussions_about_topics(text, topics):
    sentences = sent_tokenize(text)
    topic_discussions = {topic: [] for topic in topics}
    
    for sentence in sentences:
        words = set(word_tokenize(sentence.lower()))
        for topic in topics:
            if any(word in words for word in topic.lower().split()):
                topic_discussions[topic].append(sentence)
    
    return topic_discussions

def select_salient_sentences(discussions, text, symbol, year, quarter, date):
    salient_sentences = {}
    for topic, sentences in discussions.items():
        if not sentences:
            continue
        
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(sentences)
            sentence_scores = {sentence: sum(tfidf_matrix[idx].toarray()[0]) for idx, sentence in enumerate(sentences)}
            sorted_sentences = sorted(sentences, key=lambda s: sentence_scores[s], reverse=True)
            
            enhanced_sentences = []
            i = 0
            while i < len(sorted_sentences):
                sentence = sorted_sentences[i]
                if sentence.endswith('?'):
                    answer_length = 4
                    if i + 1 < len(sorted_sentences) and sorted_sentences[i + 1].endswith('?'):
                        answer_length = 3  
                    
                    answer = " ".join(sorted_sentences[i + 1:i + 1 + answer_length]) if i + answer_length < len(sorted_sentences) else " ".join(sorted_sentences[i + 1:])
                    enhanced_sentences.append((f"Q: {sentence}", f"A: {answer}", symbol, year, quarter, date))
                    i += answer_length + 1
                else:
                    enhanced_sentences.append((sentence, symbol, year, quarter, date))
                    i += 1
                    
            salient_sentences[topic] = enhanced_sentences
        except ValueError:
            salient_sentences[topic] = []
    
    return salient_sentences

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        query = request.form['query']
        
        print(f"Searching in directory: transcripts/{ticker}/")
        file_paths = glob.glob(f'transcripts/{ticker}/*.json')
        print(f"Found files: {file_paths}")
        results = []

        for file_path in file_paths:
            text, symbol, year, quarter, date = read_json_file(file_path)
            print(f"Reading file: {file_path} - Found content length: {len(text)}")
            discussions = extract_discussions_about_topics(text, [query])
            print(f"Discussions found: {discussions}")
            for topic, sentences in discussions.items():
                for sentence in sentences:
                    results.append((sentence, symbol, year, quarter, date))

        if not results:
            print("No results found for your query.")
        else:
            print(f"Results found: {len(results)}")
        
        return render_template('results.html', ticker=ticker, query=query, results=results)
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
