import os
import openai
from llama_index import download_loader, KnowledgeGraphIndex, ServiceContext

JSONReader = download_loader("JSONReader")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

def create_knowledge_graph(file_path):
    documents = JSONReader().load_data(file_path)
    service_context = ServiceContext.from_defaults()
    index = KnowledgeGraphIndex.from_documents(documents, service_context=service_context)
    return index

def process_transcripts(directory):
    knowledge_graphs = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                knowledge_graph = create_knowledge_graph(file_path)
                knowledge_graphs[file] = knowledge_graph
    
    return knowledge_graphs

# Directory containing the earnings transcripts
transcripts_directory = "transcripts/VRT"

# Create knowledge graphs for each transcript
knowledge_graphs = process_transcripts(transcripts_directory)

# Explore the knowledge graphs
for filename, graph in knowledge_graphs.items():
    print(f"Knowledge Graph for {filename}:")
    print(graph.get_knowledge_graph())
    print()

    # Optionally, you can save the knowledge graph to a file
    graph.save_to_disk(f"knowledge_graph_{filename}.json")