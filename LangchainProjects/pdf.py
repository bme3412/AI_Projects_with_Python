from langchain.document_loaders import PyPDFLoader
import os
import getpass


os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API Key:')
loader = PyPDFLoader('ABNB_10K_2023.pdf')
pages = loader.load_and_split()

from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

fass_index = FAISS.from_documents(pages,OpenAIEmbeddings())
docs = fass_index.similarity_search("Detail the revenue growth of Airbnb as reported in the 2023 10-K")
for doc in docs:
    print(str(doc.metadata['page']) + ':',doc.page_content)

import re

# Assuming PyPDFLoader, FAISS, and OpenAIEmbeddings are defined as before
loader = PyPDFLoader('ABNB_10K_2023.pdf')
pages = loader.load_and_split()

fass_index = FAISS.from_documents(pages, OpenAIEmbeddings())
docs = fass_index.similarity_search("Detail the revenue growth of Airbnb as reported in the 2023 10-K")

# Function to extract revenue figures and calculate growth
def extract_revenue_info(text):
    # Regular expressions to find revenue figures. This is a simple example and might need to be adjusted.
    revenue_matches = re.findall(r'\$\d+(?:,\d+)*(?:\.\d+)? billion', text)
    growth_matches = re.findall(r'\d+\.?\d*%', text)

    if revenue_matches and growth_matches:
        return f"Revenue for ABNB in 2023 was {revenue_matches[0]}, which grew by {growth_matches[0]}."
    else:
        return "Revenue information not found or unclear."

# Analyzing and printing the relevant information
for doc in docs:
    revenue_info = extract_revenue_info(doc.page_content)
    print(f"Page {doc.metadata['page']}: {revenue_info}")
