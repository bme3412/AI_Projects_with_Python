# incorproate all tickers

from flask import Flask, render_template, request, jsonify
import glob
import os
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


app = Flask(__name__)
nltk.download('punkt')

def get_available_tickers():
    # Assuming each ticker has its own directory under 'transcripts/'
    directories = glob.glob('transcripts/*/')
    tickers = [os.path.basename(os.path.dirname(path)) for path in directories]
    tickers.append('ALL')  # Optional: Add an option to search all tickers
    return tickers

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data.get('content', ''), data.get('symbol', ''), data.get('year', ''), data.get('quarter', ''), data.get('date', '')

def extract_discussions_about_topics(text, topics):
    sentences = sent_tokenize(text)
    topic_discussions = {topic: [] for topic in topics}
    question = None
    answer = []
    current_speaker = None

    for sentence in sentences:
        if ':' in sentence:
            parts = sentence.split(':', 1)
            current_speaker = parts[0].strip()
            sentence = parts[1].strip()

        relevant_topics = [topic for topic in topics if any(
            word in sentence.lower() for word in topic.lower().split())]
        if sentence.endswith('?'):
            if question:
                for topic in question[1]:
                    topic_discussions[topic].append(
                        (question[0], ' '.join(answer), question[2], text))
                answer = []
            question = (sentence, relevant_topics, current_speaker)
        else:
            answer.append(sentence)
            for topic in relevant_topics:
                # None for no specific answer
                topic_discussions[topic].append(
                    (sentence, None, current_speaker, text))

    if question:  # Ensure last question is processed
        for topic in question[1]:
            topic_discussions[topic].append(
                (question[0], ' '.join(answer), question[2], text))

    return topic_discussions

def get_context_sentences(sentences, query, num_before=7, num_after=7):
    query_lower = query.lower()
    context_sentences = []

    for i, sentence in enumerate(sentences):
        if any(word.lower() in sentence.lower() for word in query_lower.split()):
            start = max(0, i - num_before)
            end = min(len(sentences), i + num_after + 1)
            context_sentences.append((sentence, sentences[start:i], sentences[i+1:end]))

    return context_sentences

@app.route('/get_transcripts/<ticker>')
def get_transcripts(ticker):
    transcript_dir = f'transcripts/{ticker}'
    transcript_files = []
    
    if os.path.exists(transcript_dir):
        for file in os.listdir(transcript_dir):
            if file.endswith('.json'):
                transcript_files.append(file)
    
    return jsonify({'transcripts': transcript_files})

@app.route('/get_transcript_content/<ticker>/<path:file>')
def get_transcript_content(ticker, file):
    transcript_path = f'transcripts/{ticker}/{file}'
    
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    
    return jsonify({'error': 'Transcript not found'}), 404


@app.route('/', methods=['GET', 'POST'])
def index():
    tickers = get_available_tickers()
    if request.method == 'POST':
        ticker = request.form['ticker']
        query = request.form['query']
        file_paths = glob.glob(
            f'transcripts/{ticker}/*.json') if ticker != 'ALL' else glob.glob('transcripts/*/*.json')

        results = []
        for file_path in file_paths:
            text, symbol, year, quarter, date = read_json_file(file_path)
            discussions = extract_discussions_about_topics(text, [query])
            sentences = sent_tokenize(text)
            for topic, sentences_data in discussions.items():
                for sentence, answer, speaker, text in sentences_data:
                    context = get_context_sentences(sentences, query)
                    for content_sentence, before_sentences, after_sentences in context:
                        if content_sentence == sentence:
                            results.append((sentence, answer, speaker, symbol, year, quarter, date, before_sentences, after_sentences))
                            break

        # Sort results by date
        results.sort(key=lambda x: x[6])  # Sorting by the date element in the results tuple

        return render_template('results.html', tickers=tickers, ticker=ticker, query=query, results=results)

    return render_template('index.html', tickers=tickers)

if __name__ == '__main__':
    app.run(debug=True)