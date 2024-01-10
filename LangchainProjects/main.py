import os

from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

if __name__ == "__main__":
    pdf_path = 'q3-2023-analyst-call-transcript_clean.pdf'
    loader = PyPDFLoader(file_path = pdf_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=30,
        separator='\n'
    )

    documents = text_splitter.split_documents(documents=documents)
    
    # Your OpenAI API key
    api_key = ''

# Create an instance of OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local('faiss_index_pdf')

    new_vector_store = FAISS.load_local('faiss_index_pdf', embeddings)
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(), chain_type='stuff', retriever=new_vector_store.as_retriever()
    )

    response = qa.invoke("Which companies did the mention generative AI?")
    print(response)