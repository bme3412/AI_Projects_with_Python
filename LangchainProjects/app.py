from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

pdfs = [
    'ABNB_10K_2021.pdf',
    'ABNB_10K_2022.pdf',
    'ABNB_10K_2023.pdf'
]

annual_reports = []
for pdf in pdfs:
    loader = PyPDFLoader(pdf)
    document = loader.load()
    annual_reports.append(document)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

chunked_annual_reports = []
for annual_report in annual_reports:
    texts = text_splitter.split_documents(annual_report)

    chunked_annual_reports.append(texts)
    print(f"chunked report length: {len(texts)}")

from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings import OpenAIEmbeddings
import pinecone
import os

OPENAI_API_KEY = ''
PINECONE_API_KEY = ''
PINECONE_API_ENV = 'gcp-starter'

embeddings = OpenAIEmbeddings()
print(dir(embeddings))

# initialize pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
index = pinecone.Index('airbnb')
index_name = 'airbnb'

for chunks in chunked_annual_reports:
    vectors = embeddings.get_embeddings([chunk.page_content for chunk in chunks])
    index.upsert(vectors=vectors)


vectorstore = Pinecone.from_existing_index(index_name=index_name, embedding = embeddings)

from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm)

query = "What is the overall sentiment of Airbnb's most recent annual report? Provide some numbers."
docs = vectorstore.similarity_search(query)
result = chain.run(input_documents=docs, question=query)
print(result)