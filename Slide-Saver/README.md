
# Document Summarization Service

This Document Summarization Service is built using Flask and utilizes several technologies including Boto3, NLTK, and the LangChain Community API to process and summarize PDF documents. The service extracts text from uploaded PDF files, analyzes it with Amazon Rekognition for OCR, and then summarizes the text using a custom LangChain summarization chain.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository```
   
2. **Install dependencies:**
   ```bash
   pip install flask boto3 pdf2image Pillow nltk langchain-community```
