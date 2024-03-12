from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from flask_caching import Cache
from openai import OpenAI
import os, json
from dotenv import load_dotenv

from utility import process_transcript_file
from utility import key_reported_metrics

load_dotenv()
openAI_api_key = os.getenv('OPENAI_API_KEY')
financial_api_key = os.getenv('FINANCIAL_MODEL_PREP_API')

llm_model = OpenAI(api_key=openAI_api_key)


app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/process_vrt_files', methods=['POST'])
def process_vrt_files():
    vrt_folder = 'transcripts/VRT/2023'
    results = []

    for root, dirs, files in os.walk(vrt_folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Concatenate all 'text' fields from the 'content' list into one string
                    transcript_text = ' '.join([item['text'] for item in data[0]['content']])
                    # Now, you can call your LLM function with the compiled transcript_text
                    result_dict = key_reported_metrics(transcript_text, llm_model)
                    formatted_result = "; ".join([f"{k}: {v}" for k, v in result_dict.items()])
                    results.append({'file': file, 'result': formatted_result})

    # Adapt this part to return JSON if you're using the JS method
    return jsonify({'results': results})



if __name__ == '__main__':
    app.run(debug=True)


