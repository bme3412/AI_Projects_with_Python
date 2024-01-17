from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from llama_index import SimpleDirectoryReader, LLMPredictor, ServiceContext, GPTVectorStoreIndex
from llama_index.response.pprint_utils import pprint_response
from langchain_openai import OpenAI
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine
from werkzeug.utils import secure_filename
import os


# Initialize Flask app
app = Flask(__name__)
CORS(app)



llm = OpenAI(temperature=0, model_name='text-davinci-003',
             max_tokens=-1)  # Using LLM instead of LLMPredictor
service_context = ServiceContext.from_defaults(llm=llm)

lyft_docs = SimpleDirectoryReader(
    input_files=['data/LYFT_10K_2023.pdf']).load_data()
uber_docs = SimpleDirectoryReader(
    input_files=['data/UBER_10K_2023.pdf']).load_data()

lyft_index = GPTVectorStoreIndex.from_documents(lyft_docs)
uber_index = GPTVectorStoreIndex.from_documents(uber_docs)


# Build query engines
lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
uber_engine = uber_index.as_query_engine(similarity_top_k=3)

query_engine_tools = [
    QueryEngineTool(
        query_engine=lyft_engine,
        metadata=ToolMetadata(
            name='lyft_10k', description='Provides info about Lyft financials in 2022')
    ),
    QueryEngineTool(
        query_engine=uber_engine,
        metadata=ToolMetadata(
            name='uber_10k', description='Provides info about Uber financials in 2022')
    ),
]

s_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools)

response = s_engine.query(
    'How many and which primary countries does Uber oeprate in?')
print(response)

@app.route('/')
def index():
    return render_template('chat_interface.html')



# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5000)