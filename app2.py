import streamlit as st
from save_audio import save_audio
from configure import auth_key
import pandas as pd
from time import sleep
import urllib.request
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import requests

# AssemblyAI endpoints and headers
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
headers_auth_only = {'authorization': auth_key}
headers = {
   "authorization": auth_key,
   "content-type": "application/json"
}

# App explanation
st.title('Sentiment analysis of earning calls')
st.caption('With this app you can analyze the sentiment of earnings calls. Simply provide a YouTube link to extract audio')
st.subheader('Submit a video link:')

# Get link from user
video_url = st.text_input(label='Earnings call link', value="https://www.youtube.com/watch?v=UA-ISgpgGsk")

# Save audio locally
save_location = save_audio(video_url)

# Upload audio to AssemblyAI
CHUNK_SIZE = 5242880
def read_file(filename):
	with open(filename, 'rb') as _file:
		while True:
			data = _file.read(CHUNK_SIZE)
			if not data:
				break
			yield data

upload_response = requests.post(
	upload_endpoint,
	headers=headers_auth_only, data=read_file(save_location)
)
audio_url = upload_response.json()['upload_url']

# Start transcription job of audio file
data = {
	'audio_url': audio_url,
	'sentiment_analysis': 'True',
}
transcript_response = requests.post(transcript_endpoint, json=data, headers=headers)
transcript_id = transcript_response.json()['id']
polling_endpoint = transcript_endpoint + "/" + transcript_id

# Waiting for transcription to be done
status = 'submitted'
while status != 'completed':
	sleep(5)
	polling_response = requests.get(polling_endpoint, headers=headers)
	status = polling_response.json()['status']

# Display transcript
st.sidebar.header('Transcript of the earnings call')
transcript = polling_response.json()['text']
st.sidebar.markdown(transcript)

# Sentiment analysis response
sar = polling_response.json()['sentiment_analysis_results']

# Save to a dataframe for ease of visualization
sen_df = pd.DataFrame(sar)

# Map sentiment to numeric values and add a proxy for time
sentiment_mapping = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}
sen_df['sentiment_numeric'] = sen_df['sentiment'].map(sentiment_mapping)
sen_df['proxy_time'] = sen_df.index
sen_df['cumulative_sentiment'] = sen_df['sentiment_numeric'].cumsum()

# Get the title of this video
with urlopen(video_url) as url:
	s = url.read()
	soup = BeautifulSoup(s, 'html.parser')
	title = soup.title.string

st.header(title)

# Visualizations
st.markdown("### Number of sentences: " + str(sen_df.shape[0]))
grouped = pd.DataFrame(sen_df['sentiment'].value_counts()).reset_index()
grouped.columns = ['sentiment','count']

# ... Existing visualization code ...

# Time Series Line Plot
fig = px.line(sen_df, x='proxy_time', y='cumulative_sentiment', title='Sentiment Over Time', labels={'proxy_time':'Index as Time Proxy', 'cumulative_sentiment':'Cumulative Sentiment'})
st.plotly_chart(fig)
