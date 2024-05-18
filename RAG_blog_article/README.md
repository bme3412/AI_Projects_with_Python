# Document Processing Flask App

This is a Flask application that processes uploaded documents (`.txt`, `.docx`, `.pdf`) to extract text, summarize the content, categorize it, and generate CSV and Word documents. The application also returns the results in a zipped file.

## Features

- Upload `.txt`, `.docx`, or `.pdf` files.
- Extract text from uploaded documents.
- Summarize and categorize the content using OpenAI's GPT-4 model.
- Generate and download CSV and Word documents containing the raw text, summary, and category.
- Display the results in a web interface.

## Requirements

- Python 3.7+
- Flask
- pandas
- python-docx
- PyPDF2
- zipfile
- openai
- llama-index
- langchain

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/document-processing-flask-app.git
    cd document-processing-flask-app
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your OpenAI API key:

    ```bash
    export OPENAI_API_KEY='your_openai_api_key'
    ```

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Open your web browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

3. Upload a `.txt`, `.docx`, or `.pdf` file and click "Upload".

4. The application will process the file, summarize and categorize the content, and display the results.

5. Download the results as a zip file containing the CSV and Word documents.
