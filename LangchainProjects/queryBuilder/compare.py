from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Import your existing code modules
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

app = Flask(__name__)
CORS(app)

# Load two documents
pdf_paths = ['Q2_NFLX.pdf', 'Q3_NFLX.pdf']
documents = []
for path in pdf_paths:
    loader = PyPDFLoader(file_path=path)
    documents += loader.load()

# Process documents
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
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #eaeaea;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .form-container {
                        background-color: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        width: 50%;
                        max-width: 600px;
                    }
                    label {
                        font-size: 20px;
                        color: #333;
                        display: block;
                        margin-bottom: 10px;
                    }
                    input[type="text"] {
                        width: calc(100% - 20px);
                        padding: 15px;
                        margin-bottom: 20px;
                        border-radius: 5px;
                        border: 1px solid #ccc;
                        font-size: 16px;
                        box-sizing: border-box;
                    }
                    input[type="submit"] {
                        width: 100%;
                        background-color: #4CAF50;
                        color: white;
                        padding: 15px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 18px;
                        transition: background-color 0.3s;
                    }
                    input[type="submit"]:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <div class="form-container">
                    <form action="/query" method="post">
                        <label for="query">Enter your query about NFLX Q2 and Q3 earnings:</label>
                        <p style="font-size: 14px; color: grey;">Example: What did the company say about the rollout of paid sharing in Q2 and Q3?</p>
                        <p style="font-size: 14px; color: grey;">Example: What was pricing growth and subscriber growth in Q2 and Q3 for NFLX? Please provide numbers.</p>
                        <input type="text" id="query" name="query">
                        <input type="submit" value="Submit">
                    </form>
                </div>
            </body>
            </html>'''



@app.route('/query', methods=['POST'])
def handle_query():
    query = request.form['query']
    
    if not query:
        return 'No query provided', 400

    try:
        # Custom logic for comparing across documents
        response_dict = qa.invoke(query)
        response_result = response_dict.get('result', 'No result found')  # Extracts only the 'result' part

        response_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Query Response</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #eaeaea;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        height: 100vh;
                    }}
                    .container {{
                        width: 50%;
                        max-width: 700px;
                        margin-top: 30px;
                    }}
                    .box {{
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #333;
                        font-size: 24px;
                        margin-bottom: 10px;
                    }}
                    p {{
                        font-size: 18px;
                        color: #666;
                        line-height: 1.6;
                    }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background-color: #007BFF;
                        color: white;
                        border-radius: 5px;
                        text-decoration: none;
                        font-size: 16px;
                        transition: background-color 0.3s;
                    }}
                    a:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="box">
                        <h1>Your Query</h1>
                        <p>{query}</p>
                    </div>
                    <div class="box">
                        <h1>Response</h1>
                        <p>{response_result}</p>
                    </div>
                    <a href="/">Ask another query</a>
                </div>
            </body>
            </html>
        '''
        return response_html
    except Exception as e:
        return f'An error occurred: {e}', 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
