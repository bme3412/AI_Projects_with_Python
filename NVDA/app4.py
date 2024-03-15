import streamlit as st
import os
import pickle
import logging
from llama_index import Document, GPTSimpleVectorIndex, ServiceContext, StorageContext, load_index_from_storage
from llama_index.vector_stores import FAISSVectorStore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
DOCS_DIR = os.path.abspath("./")

def load_document(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return Document(text)

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
    document = load_document(doc_file_path)

    if document:
        logger.info(f"Document loaded successfully")
        st.success("Document loaded successfully!")
    else:
        st.warning("Failed to load document!", icon="⚠️")
        logger.warning("Failed to load document")
else:
    st.warning("Please upload a Word or PDF document.", icon="⚠️")

# Index Construction
index_path = "index"
vector_store_path = "vector_store"

with st.sidebar:
    use_existing_index = st.radio("Use existing index if available", ["Yes", "No"], horizontal=True)

index_exists = os.path.exists(index_path)
index = None

if use_existing_index == "Yes" and index_exists:
    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    index = load_index_from_storage(storage_context)
    with st.sidebar:
        st.success("Existing index loaded successfully.")
else:
    with st.sidebar:
        if uploaded_file is not None and document:
            with st.spinner("Constructing index..."):
                service_context = ServiceContext.from_defaults()
                index = GPTSimpleVectorIndex.from_documents([document], service_context=service_context)
                logger.info("Index constructed")

            with st.spinner("Saving index"):
                storage_context = StorageContext.from_defaults(persist_dir=index_path)
                index.storage_context.persist(persist_dir=index_path)
            st.success("Index constructed and saved.")
        else:
            st.warning("No documents available to process!", icon="⚠️")
            logger.warning("No documents available to process")

# Chat Interface
st.subheader("Chat with your AI Assistant, Lionel!")

if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_prompt(user_input):
    return f"You are a helpful AI assistant named Lionel. You will reply to questions only based on the context that you are provided. If something is out of context, you will refrain from replying and politely decline to respond to the user.\n\nUser: {user_input}\nAssistant:"

user_input = st.text_input("Ask a question about the document:")

if user_input and index is not None:
    st.session_state.messages.append({"role": "user", "content": user_input})

    query_engine = index.as_query_engine()
    response = query_engine.query(user_input)

    st.write("User:", user_input)
    message_placeholder = st.empty()
    full_response = str(response)

    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})