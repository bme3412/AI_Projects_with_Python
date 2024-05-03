import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import boto3
from pdf2image import convert_from_path
from io import BytesIO
import nltk
from langchain_community.llms import OpenAI
from langchain.docstore.document import Document
from langchain.chains import MapReduceDocumentsChain, StuffDocumentsChain, LLMChain
from langchain.prompts import PromptTemplate

app = Flask(__name__)
upload_folder = './uploads/'
app.config['UPLOAD_FOLDER'] = upload_folder
os.makedirs(upload_folder, exist_ok=True)

nltk.download('punkt')

@app.route('/')
def index():
    return render_template('index.html')

def process_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    rekognition = boto3.client('rekognition')
    page_content = []
    for i, page in enumerate(pages, start=1):
        img_byte_arr = BytesIO()
        page.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        response = rekognition.detect_text(Image={'Bytes': img_byte_arr})
        text = ' '.join([d['DetectedText'] for d in response['TextDetections'] if d['Type'] == 'LINE'])
        page_content.append({'page': i, 'content': text})
    return page_content, len(pages)

def custom_summarize(llm, docs):
    map_template = """
    Extract key financial metrics from the following documents: {docs}
    Focus on the most recent and relevant information. Only include reference for the current and prior year or prior quarter periods
    Metrics to include:
    - Revenue growth
    - Profit margins
    - EPS details
    - Cash flow
    - Outlook
    Provide numerical values where available, and avoid repeating the same information multiple times.
    """
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    reduce_template = """
    Consolidate the financial summaries into a concise overview, highlighting the most important and up-to-date metrics and outlook from these documents: {docs}
    Organize the information in a clear and logical manner, removing any duplicated or outdated data.
    Only include reference for the current and prior year or prior quarter periods
    Metrics to include:
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = StuffDocumentsChain(llm_chain=LLMChain(llm=llm, prompt=reduce_prompt), document_variable_name="docs")

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_chain,
        document_variable_name="docs"
    )
    return map_reduce_chain.run(docs)  # Change invoke() to run() and return the actual summary text

def paginate_documents(docs, batch_size=5):
    for i in range(0, len(docs), batch_size):
        yield docs[i:i + batch_size]

@app.route('/process_pdf', methods=['POST'])
def handle_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    pdf_file = request.files['pdf_file']
    filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(pdf_path)
    page_content, num_pages = process_pdf(pdf_path)
    docs = [Document(page_content=page['content']) for page in page_content]
    llm = OpenAI()
    summaries = [custom_summarize(llm, doc_batch) for doc_batch in paginate_documents(docs)]
    final_summary = " ".join(summaries)
    os.remove(pdf_path)  # Clean up the file after processing
    structured_content = [{'page': page['page'], 'content': page['content']} for page in page_content]
    return jsonify({'summary': final_summary, 'num_pages': num_pages, 'page_content': structured_content})

if __name__ == '__main__':
    app.run(debug=True)