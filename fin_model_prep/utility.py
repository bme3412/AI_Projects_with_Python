from openai import OpenAI

client = OpenAI()
import json

def summarize_text(text):
    response = client.completions.create(engine="text-davinci-003",  # Check for the latest and most suitable model
    prompt="Summarize the following text:\n\n" + text,
    max_tokens=150)
    summary = response.choices[0].text.strip()
    return summary

def key_reported_metrics(transcript, llm_model=client):
    prompt = f"""
    Analyze the provided earnings call transcript and extract the following financial information:

    1. Revenue:
       - Total revenue for the reported period
       - Revenue growth percentage compared to the same period last year

    2. Gross Profit:
       - Gross profit for the reported period
       - Gross margin percentage

    3. Operating Income/EBIT (Earnings Before Interest and Taxes):
       - Operating income/EBIT for the reported period
       - Operating margin percentage

    4. EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization):
       - EBITDA for the reported period
       - EBITDA margin percentage

    5. Net Income:
       - Net income for the reported period
       - Net income growth percentage compared to the same period last year

    6. Free Cash Flow (FCF):
       - Free cash flow for the reported period
       - Free cash flow growth percentage compared to the same period last year

    Please provide the extracted information in a clear, concise manner. If any of the requested information is not explicitly mentioned in the transcript, indicate that it was not found.

    Remember to use the exact terms and figures mentioned in the transcript to avoid misinterpretation. If there are any forward-looking statements or projections, include them separately from the reported figures.

    Transcript:
    {transcript}
    """

    # Call the LLM model with the prompt
    response = llm_model.create_completion(prompt=prompt)
    return response.choices[0].text.strip()

def process_transcript_file(file_path):
    with open(file_path, 'r') as file:
        transcript_data = json.load(file)
    # Assuming the JSON structure contains a key 'transcript' with the transcript text
    transcript_text = transcript_data.get('transcript', '')
    return key_reported_metrics(transcript_text)