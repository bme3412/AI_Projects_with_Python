import os
import PyPDF2
from flask import Flask, request, render_template
import openai


def get_pdf_path(ticker):
    pdf_directory = ''  # Replace with your PDF directory
    pdf_filename = f"{ticker}.pdf"
    pdf_path = os.path.join(pdf_directory, pdf_filename)
    if os.path.exists(pdf_path):
        return pdf_path
    else:
        return None  # Or handle this case as needed

def convert_pdf_to_text(path):
    if path is None:
        return None  # Or handle this case as needed

    with open(path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages
        text = ""
        for page in range(num_pages):
            page_obj = pdf_reader.getPage(page)
            text += page_obj.extractText()
        return text


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        pdf_path = get_pdf_path(ticker)  # Function to map ticker to PDF
        pdf_content = convert_pdf_to_text(pdf_path)  # Convert PDF to text
        openai_response = query_openai(pdf_content)  # Query OpenAI with PDF content
        return render_template('results.html', response=openai_response)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)