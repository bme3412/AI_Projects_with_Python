
# Document Summarization Service

This Document Summarization Service is built using Flask and utilizes several technologies including Boto3, NLTK, and the LangChain Community API to process and summarize PDF documents. The service extracts text from uploaded PDF files, analyzes it with Amazon Rekognition for OCR, and then summarizes the text using a custom LangChain summarization chain.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   
2. **Install dependencies:**
   ```bash
   pip install flask boto3 pdf2image Pillow nltk langchain-community

3. **Download NLTK packages:**
   ```bash
   import nltk
   nltk.download('punkt')

4. **Set up environment variables:**
   Ensure you have configured your AWS credentials which are required for Boto3 to interact with AWS services.

## Usage

1. **Start the Server:**
   ```bash
   python app.py

2. **Access the service::**
   Open your web browser and go to http://localhost:5000/. Upload a PDF file through the provided interface.
   
## Features
+ **PDF Text Extraction:** Converts PDF documents into images per page and uses OCR to extract text.
+ **Text Summarization:** Implements a custom summarization chain using LangChain to provide insights from the extracted text.
+ **Batch Processing:** Supports processing documents in batches to efficiently handle larger documents.

## API Endpoints
+ GET /: Home page.
+ POST /process_pdf: Endpoint to upload a PDF file and retrieve summarized content.

   
