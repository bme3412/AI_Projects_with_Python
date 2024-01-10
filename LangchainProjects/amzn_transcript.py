from PyPDF2 import PdfReader
import openai
openai.api_key = ''

def read_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

pdf_text = read_pdf('q3-2023-analyst-call-transcript_clean.pdf')
#print(pdf_text[:500])
#print(pdf_text)
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter



chunk_size=1000
chunk_overlap=150

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    length_function=len
)

#docs = text_splitter.split_documents(pdf_text)

#print(len(docs))
from langchain_community.document_loaders import PyPDFLoader
loaders = [PyPDFLoader('q3-2023-analyst-call-transcript_clean.pdf')]
docs = []
for loader in loaders:
    docs.extend(loader.load())

    # Define the Text Splitter 
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1500,
    chunk_overlap = 150
)

#Create a split of the document using the text splitter
splits = text_splitter.split_documents(docs)

from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

embedding = OpenAIEmbeddings()

persist_directory = 'docs/chroma/'

# Create the vector store
vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=persist_directory
)

print(vectordb._collection.count())
question = "what did they say about regression in the third lecture?"

docs = vectordb.similarity_search(question,k=5)


# Print the metadata of the similarity search result
for doc in docs:
    print(doc.metadata)

print(docs[4].page_content)