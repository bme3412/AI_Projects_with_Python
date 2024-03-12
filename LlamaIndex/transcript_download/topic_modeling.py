import os
import json
import openai
import gensim
from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from llama_index import download_loader, KnowledgeGraphIndex, ServiceContext

JSONReader = download_loader("JSONReader")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY


def create_knowledge_graph(file_path):
    documents = JSONReader().load_data(file_path)
    service_context = ServiceContext.from_defaults()
    index = KnowledgeGraphIndex.from_documents(
        documents, service_context=service_context)
    return index


def process_transcripts(directory):
    knowledge_graphs = {}
    transcripts = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    transcript_data = json.load(f)
                    if isinstance(transcript_data, list) and isinstance(transcript_data[0], dict):
                        transcript_text = ' '.join(item['text'] for item in transcript_data if 'text' in item)
                    elif isinstance(transcript_data, dict) and 'text' in transcript_data:
                        transcript_text = transcript_data['text']
                    else:
                        print(f"Skipping file {file} due to incompatible format.")
                        continue
                    
                    transcripts.append(transcript_text)
                    knowledge_graph = create_knowledge_graph(file_path)
                    knowledge_graphs[file] = knowledge_graph

    return knowledge_graphs, transcripts


def perform_topic_modeling(transcripts, num_topics=5):
    # Preprocess the transcripts
    stop_words = set(stopwords.words('english'))
    tokenized_transcripts = [
        [word.lower() for word in word_tokenize(transcript)
         if word.lower() not in stop_words]
        for transcript in transcripts
    ]

    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(tokenized_transcripts)
    corpus = [dictionary.doc2bow(transcript)
              for transcript in tokenized_transcripts]

    # Check if the corpus is empty
    if not corpus:
        print("Empty corpus. Skipping topic modeling.")
        return None

    # Train the topic model (LDA)
    lda_model = gensim.models.LdaMulticore(
        corpus=corpus, id2word=dictionary, num_topics=num_topics)

    return lda_model


# Directory containing the earnings transcripts
transcripts_directory = "transcripts/VRT/2023"

# Create knowledge graphs for each transcript and retrieve the transcript texts
knowledge_graphs, transcripts = process_transcripts(transcripts_directory)

# Perform topic modeling on the transcripts
num_topics = 5  # Specify the desired number of topics
lda_model = perform_topic_modeling(transcripts, num_topics)

# Analyze and interpret the topics
print("Topic Modeling Results:")
for idx, topic in lda_model.print_topics(-1):
    print(f"Topic {idx}: {topic}")

# Assign topics to documents
for i, doc in enumerate(transcripts):
    doc_lda = lda_model[lda_model.id2word.doc2bow(doc.split())]
    # Print the first 100 characters of the document
    print(f"\nDocument {i}: {doc[:100]}...")
    print(f"Topic distribution: {doc_lda}")

# Explore the knowledge graphs
for filename, graph in knowledge_graphs.items():
    print(f"\nKnowledge Graph for {filename}:")
    print(graph.get_knowledge_graph())

    # Optionally, you can save the knowledge graph to a file
    graph.save_to_disk(f"knowledge_graph_{filename}.json")
