import streamlit as st
import os
import pickle
import logging
from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders import Docx2txtLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
DOCS_DIR = os.path.abspath("./")

def load_document(file_path):
    try:
        if file_path.lower().endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif file_path.lower().endswith(".pdf"):
            loader = UnstructuredFileLoader(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path}")
            return None
        
        documents = loader.load()
        logger.info(f"Loaded document: {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading document: {file_path}")
        logger.error(f"Exception: {str(e)}")
        return None

# Load the Word or PDF document
uploaded_file = st.file_uploader("Upload a Word or PDF document", type=["docx", "pdf"])

if uploaded_file is not None:
    # Get the file extension
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Save the uploaded file temporarily with the correct extension
    with open(f"temp_doc{file_extension}", "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Load the uploaded document
    doc_file_path = f"temp_doc{file_extension}"
    raw_documents = load_document(doc_file_path)
    
    if raw_documents:
        logger.info(f"Document loaded successfully")
        st.success("Document loaded successfully!")
    else:
        st.warning("Failed to load document!", icon="⚠️")
        logger.warning("Failed to load document")
else:
    st.warning("Please upload a Word or PDF document.", icon="⚠️")
############################################
# Component #2 - Embedding Model and LLM
############################################

from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings

# make sure to export your NVIDIA AI Playground key as NVIDIA_API_KEY!
llm = ChatNVIDIA(model="mixtral_8x7b")
document_embedder = NVIDIAEmbeddings(model="nvolveqa_40k", model_type="passage")
query_embedder = NVIDIAEmbeddings(model="nvolveqa_40k", model_type="query")

############################################
# Component #3 - Vector Database Store
############################################


from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with st.sidebar:
    # Option for using an existing vector store
    use_existing_vector_store = st.radio("Use existing vector store if available", ["Yes", "No"], horizontal=True)

# Path to the vector store file
vector_store_path = "vectorstore.pkl"


# Check for existing vector store file
vector_store_exists = os.path.exists(vector_store_path)
vectorstore = None
if use_existing_vector_store == "Yes" and vector_store_exists:
    with open(vector_store_path, "rb") as f:
        vectorstore = pickle.load(f)
    with st.sidebar:
        st.success("Existing vector store loaded successfully.")
else:
    with st.sidebar:
        if uploaded_file is not None and raw_documents:
            with st.spinner("Splitting documents into chunks..."):
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                documents = text_splitter.split_documents(raw_documents)
                logger.info(f"Split {len(raw_documents)} raw documents into {len(documents)} chunks")

            with st.spinner("Adding document chunks to vector database..."):
                vectorstore = FAISS.from_documents(documents, document_embedder)
                logger.info("Vector store created")

            with st.spinner("Saving vector store"):
                with open(vector_store_path, "wb") as f:
                    pickle.dump(vectorstore, f)
            st.success("Vector store created and saved.")
        else:
            st.warning("No documents available to process!", icon="⚠️")
            logger.warning("No documents available to process")
############################################
# Component #4 - LLM Response Generation and Chat
############################################

st.subheader("Chat with your AI Assistant, Lionel!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages(
    [("system", "You are a helpful AI assistant named Lionel. You will reply to questions only based on the context that you are provided. If something is out of context, you will refrain from replying and politely decline to respond to the user."), ("user", "{input}")]
)
user_input = st.chat_input("Ask a question about the document:")
llm = ChatNVIDIA(model="mixtral_8x7b")

chain = prompt_template | llm | StrOutputParser()

if user_input and vectorstore is not None:
    st.session_state.messages.append({"role": "user", "content": user_input})
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    context = ""
    for doc in docs:
        context += doc.page_content + "\n\n"

    augmented_user_input = "Context: " + context + "\n\nQuestion: " + user_input + "\n"

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for response in chain.stream({"input": augmented_user_input}):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})