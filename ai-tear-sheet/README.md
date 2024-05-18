# AI-Tearsheet

## Overview
AI-Tearsheet is a web application designed to fetch and display financial data for companies, providing comprehensive insights using various APIs. The application integrates with Chart.js for dynamic chart rendering, and it features a seamless user experience with Flask.

## Features
- **Financial Data Fetching**: Retrieves company profiles, annual returns, price targets, consensus data, income statements, balance sheets, and cash flow statements.
- **Dynamic Chart Rendering**: Utilizes Chart.js to display price data over various time periods.
- **Transcripts Analysis**: Fetches and analyzes earnings call transcripts using OpenAI's GPT-4-turbo model, providing detailed management outlook and guidance.
- **Custom Filters and Formatting**: Implements custom Jinja filters for formatting numbers, percentages, and dates.


## Installation
1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/ai-tearsheet.git
    cd ai-tearsheet
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory and add your API keys:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    FINANCIAL_MODEL_PREP_API_KEY=your_fmp_api_key
    ```

5. **Run the application**:
    ```bash
    flask run
    ```

## Usage
- **Home Page**: Displays company data including profile, annual returns, price targets, and consensus data.
- **Income Statement, Balance Sheet, and Cash Flow**: Accessible via respective buttons and displays detailed financial statements.
- **Transcripts**: Fetches and displays earnings call transcripts, allowing you to generate and analyze prompts using the OpenAI GPT-4-turbo model.


## Acknowledgements
- **Financial Modeling Prep**: For providing comprehensive financial data APIs.
- **OpenAI**: For the powerful GPT-4-turbo model used in transcript analysis.
- **Chart.js**: For dynamic and interactive chart rendering.
]

