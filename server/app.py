import io
import os
from PyPDF2 import PdfReader
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Function to split text into chunks
def split_into_chunks(text, max_length):
    words = text.split()
    for i in range(0, len(words), max_length):
        yield ' '.join(words[i:i+max_length])

app = Flask(__name__,
            template_folder='../front_end/templates',
            static_folder='../front_end/static')

# Set your OpenAI API key


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload route hit")  # Log when route is accessed
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        pdfReader = PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in pdfReader.pages:
            text += page.extract_text()

        topics = ["AWS and cloud spend", "margins", "ecommerce", "holiday season", "AI"]
        chunk_size = 250  # Adjust this based on experimentation
        summaries = []

        for topic in topics:
            topic_summary = []
            for chunk in split_into_chunks(text, chunk_size):
                prompt = (
                    f"Summarize information about '{topic}' in this text:\n\n"
                    + chunk
                )
                response = client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=100  # Reduced for conciseness
                )
                summary = response.choices[0].text.strip()
                if summary:  # Only add the summary if it's not empty
                    topic_summary.append(summary)

            if topic_summary:
                summaries.append(f"{topic}: {' '.join(topic_summary)}")

        full_summary = '\n'.join(summaries)
        return jsonify({'summary': full_summary})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run(debug=True)
