from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Import your existing code modules
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Load your documents and prepare the vector store outside of the endpoint
# to avoid reloading it on every request.
pdf_path = 'q3-2023-analyst-call-transcript_clean.pdf'
loader = PyPDFLoader(file_path=pdf_path)
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator='\n')
documents = text_splitter.split_documents(documents=documents)

# Your OpenAI API key
api_key = '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'

embeddings = OpenAIEmbeddings(openai_api_key=api_key)
vector_store = FAISS.from_documents(documents, embeddings)
vector_store.save_local('faiss_index_pdf')

new_vector_store = FAISS.load_local('faiss_index_pdf', embeddings)
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=new_vector_store.as_retriever())

@app.route('/')
def home():
    return '''<!DOCTYPE html>
            <html>
            <head>
                <title>Query Form</title>
            </head>
            <body>
                <form action="/query" method="post">
                    <label for="query">Enter your query:</label><br>
                    <input type="text" id="query" name="query"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
            </html>'''



@app.route('/query', methods=['POST'])
def handle_query():
    query = request.form['query']
    
    if not query:
        return 'No query provided', 400

    try:
        response = qa.invoke(query)
        return f'''<h1>Response</h1>
                <p>{response}</p>
                <a href="/">Ask another query</a>'''
    except Exception as e:
        return f'An error occurred: {e}', 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

