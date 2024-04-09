from flask import Flask, render_template, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader, Document, ServiceContext
from llama_index.llms.langchain import LangChainLLM
from llama_index.core import PromptTemplate
from langchain import OpenAI
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

load_dotenv()
FINANCIAL_MODEL_PREP_API = os.getenv('FINANCIAL_MODEL_PREP_API')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

uri = f"mongodb+srv://erhardbr:{MONGODB_PASSWORD}@serverlessinstance0.6v1u89n.mongodb.net/?retryWrites=true&w=majority&appName=ServerlessInstance0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['tech_transcripts']
collection = db['tech']

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokenized_text = nltk.word_tokenize(text.lower())
    filtered_text = [word for word in tokenized_text if word not in stop_words]
    return ' '.join(filtered_text)

def create_index(transcripts):
    documents = [Document(text=t['content']) for t in transcripts]
    embedding = OpenAIEmbedding()
    llm = OpenAI(temperature=0, model_name="text-davinci-002", max_tokens=1000)
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embedding=embedding, llm=llm)
    return index

def perform_semantic_search(index, query):
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcripts')
def transcripts():
    transcripts = list(collection.find())
    return render_template('transcripts.html', transcripts=transcripts)

@app.route('/transcripts/<ticker>')
def transcript_detail(ticker):
    transcripts = list(collection.find({'symbol': ticker}))
    parsed_transcripts = []
    for transcript in transcripts:
        content = transcript['content']
        lines = content.split('\n')
        current_speaker = None
        current_content = []
        for line in lines:
            if ':' in line:
                speaker, text = line.split(':', 1)
                if current_speaker:
                    parsed_transcripts.append({
                        'speaker': current_speaker,
                        'content': ' '.join(current_content)
                    })
                current_speaker = speaker.strip()
                current_content = [text.strip()]
            else:
                current_content.append(line.strip())
        if current_speaker:
            parsed_transcripts.append({
                'speaker': current_speaker,
                'content': ' '.join(current_content)
            })
    return render_template('transcript_detail.html', ticker=ticker, transcripts=parsed_transcripts)

@app.route('/search', methods=['GET', 'POST'])
def semantic_search():
    if request.method == 'POST':
        selected_tickers = request.form.getlist('tickers')
        query = request.form['query']
        transcripts = list(collection.find({'symbol': {'$in': selected_tickers}}))
        
        index = create_index(transcripts)
        search_results = perform_semantic_search(index, query)
        
        return render_template('search_results.html', query=query, search_results=search_results)
    else:
        tickers = collection.distinct('symbol')
        return render_template('search.html', tickers=tickers)

if __name__ == '__main__':
    app.run()