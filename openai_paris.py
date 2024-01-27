
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('#'))



# Define the conversation context and your specific question
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "List the top 6 things to do in Saint-Germain-des-Prés, Paris, including the address and a brief description for each."}
]

# Get the response from OpenAI
response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=conversation
)
response_text = response.choices[0].message.content
# Splitting the response text into entries
entries = response_text.strip().split('\n\n')

# Parsing each entry into structured data
activities = []
for entry in entries:
    if '- Address:' in entry:
        # Splitting each entry into name, address, and description
        parts = entry.split(' - Address: ')
        name = parts[0].split('. ')[1]
        if '. ' in parts[1]:
            address, description = parts[1].split('. ', 1)
        else:
            address = parts[1]
            description = "Description not provided."
        activities.append({'Name': name, 'Address': address, 'Description': description})

# Create a DataFrame
df = pd.DataFrame(activities)

# Save the DataFrame to a CSV file
df.to_csv('saint_germain_activities.csv', index=False)

print("Data saved to saint_germain_activities.csv")