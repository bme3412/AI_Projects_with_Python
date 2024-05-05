# Earnings Call Analyzer

Earnings Call Analyzer is a Flask web application that allows users to query financial earnings call transcripts for specific topics and tickers. The application utilizes natural language processing techniques to extract relevant discussions and provide insights into the most discussed topics during earnings calls.

## Installation

To set up the Earnings Call Analyzer locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/earnings-call-analyzer.git

2. Navigate to the project directory:
  ```bash
   cd earnings-call-analyzer

3. Install the required Python packages:
  ```bash
   pip install -r requirements.txt

## Usage
To start the server, run:
```bash
   python app.py


Once the server is running, access the application by navigating to http://127.0.0.1:5000/ in your web browser.

How to Use:
Select a ticker from the available list or choose ALL to search across all tickers.
Enter a topic or keyword you are interested in.
Submit the query to retrieve discussions related to your topic from the earnings call transcripts.
Results will include the context of the discussions, highlighting the sentences that mention your query alongside responses and metadata.
