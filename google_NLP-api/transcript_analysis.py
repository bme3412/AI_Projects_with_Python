import json
from google.cloud import language_v1

def analyze_transcript_entities(transcript):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=transcript, type_=language_v1.Document.Type.PLAIN_TEXT)

    response = client.analyze_entities(request={'document': document})

    for entity in response.entities:
        print(f"Entity: {entity.name}")
        print(f"Type: {language_v1.Entity.Type(entity.type_).name}")
        print(f"Salience: {entity.salience}")
        print("=" * 40)

def extractive_summarization(transcript, num_sentences=3):
    sentences = transcript.split(". ")
    sentence_scores = []

    for sentence in sentences:
        words = sentence.split()
        score = len(words)
        sentence_scores.append((sentence, score))

    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    summary_sentences = [sentence for sentence, _ in sentence_scores[:num_sentences]]
    summary = ". ".join(summary_sentences)

    return summary

# Load the JSON file
with open("GOOGL_Q4_2023.json", "r") as file:
    data = json.load(file)

# Extract the transcript content from the JSON data
transcript = data["content"]

# Analyze the transcript entities
analyze_transcript_entities(transcript)

# Generate an extractive summary
summary = extractive_summarization(transcript)
print("Summary:")
print(summary)