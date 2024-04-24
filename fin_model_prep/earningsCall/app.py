from flask import Flask, render_template, request, redirect, url_for
import requests
from dotenv import load_dotenv
import os
import pandas as pd
from openai import OpenAI
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

app = Flask(__name__)
load_dotenv()
FINANCIAL_MODEL_API = os.getenv('FINANCIAL_MODEL_API_KEY')
OPENAI_API_KEY= os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

embed_model = OpenAIEmbedding()
splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model)
base_splitter = SentenceSplitter(chunk_size=512)
llm = ChatOpenAI(model_name="gpt-4-turbo")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symbol = request.form['symbol']
        period = request.form['period']
        return redirect(url_for('earnings', symbol=symbol, period=period))
    return render_template('home.html')

@app.route('/earnings/<string:symbol>/<string:period>')
def earnings(symbol, period):
    api_key = FINANCIAL_MODEL_API
    url = f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?quarter={period}&apikey={api_key}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            symbol = data[0]['symbol']
            quarter = data[0]['quarter']
            year = data[0]['year']
            transcript = data[0]['content']
            
            # Save the transcript to a text file
            output_file = f"{symbol}_{quarter}_{year}.txt"
            with open(output_file, 'w') as f:
                f.write(transcript)
            
            # Load documents
            documents = SimpleDirectoryReader(input_files=[output_file]).load_data()
            
            # Split documents into nodes
            nodes = splitter.get_nodes_from_documents(documents)
            
            # Create an empty DataFrame to store the nodes, summaries, and categories
            df = pd.DataFrame(columns=["Raw_Text", "Summary", "Category"])
            
            # Generate summary and category for each node in sequential order
            for i, node in enumerate(nodes, start=1):
                summary_query = f"Could you summarize the following text? Return your response which covers the key points and does not miss anything important, please. No need to start with 'The text discusses', etc.\n\n{node.text}"
                summary_result = llm([HumanMessage(content=summary_query)])
                summary = summary_result.content
                
                category_query = f"Please provide a short category or topic for the following summary:\n\n{summary}"
                category_result = llm([HumanMessage(content=category_query)])
                category = category_result.content
                
                node_df = pd.DataFrame({"Raw_Text": [node.text], "Summary": [summary], "Category": [category]})
                df = pd.concat([df, node_df], ignore_index=True)
            
            # Add company name, quarter, and year columns to the DataFrame
            df["Company"] = symbol
            df["Quarter"] = quarter
            df["Year"] = year
            
            # Save the DataFrame to a CSV file
            output_file = f"{symbol}_{quarter}_{year}.csv"
            df.to_csv(output_file, index=False)
            
            return render_template('earnings.html', symbol=symbol, quarter=quarter, year=year, transcript=transcript, data=df.to_dict('records'))
        else:
            return "No earnings call transcript found for the specified symbol and period."
    else:
        return "Failed to retrieve earnings call transcript."

if __name__ == '__main__':
    app.run(debug=True)