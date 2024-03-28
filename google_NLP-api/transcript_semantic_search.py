import json
from google.cloud import language_v1

def analyze_transcript_entities(transcript):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=transcript, type_=language_v1.Document.Type.PLAIN_TEXT)

    response = client.analyze_entities(request={'document': document})

    entities = []
    for entity in response.entities:
        entities.append({
            "name": entity.name,
            "type": language_v1.Entity.Type(entity.type_).name,
            "salience": entity.salience
        })

    return entities

def semantic_search(query, search_index, top_k=3):
    query_entities = analyze_transcript_entities(query)

    relevant_transcripts = []
    for entry in search_index:
        entry_score = 0
        for query_entity in query_entities:
            for entry_entity in entry["entities"]:
                if query_entity["name"].lower() == entry_entity["name"].lower():
                    entry_score += entry_entity["salience"]
                    break
        if entry_score > 0:
            relevant_transcripts.append({"entry": entry, "score": entry_score})

    relevant_transcripts.sort(key=lambda x: x["score"], reverse=True)
    top_results = relevant_transcripts[:top_k]

    return top_results

# Load the JSON files and build the search index
search_index = []
for filename in ["GOOGL_Q4_2023.json", "AAPL_Q1_2024.json", "NVDA_Q3_2023.json"]:
    with open(filename, "r") as file:
        data = json.load(file)
        transcript = data["content"]
        entities = analyze_transcript_entities(transcript)
        search_index.append({
            "filename": filename,
            "transcript": transcript,
            "entities": entities
        })

# Perform semantic search
query = "Alphabet's financial performance and future outlook"
results = semantic_search(query, search_index)

# Print the search results
for result in results:
    print(f"File: {result['entry']['filename']}")
    print(f"Relevance Score: {result['score']}")
    print(f"Transcript Snippet: {result['entry']['transcript'][:200]}...")
    print("=" * 40)