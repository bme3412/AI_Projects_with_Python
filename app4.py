import streamlit as st
import os
import subprocess
import pandas as pd
import requests
from pytube import YouTube
from google_config import yt_auth_key
from configure import assemblyAI_auth_key
from googleapiclient.discovery import build
import json
import plotly.express as px
import plotly.graph_objects as go
from time import sleep

# Initialize AssemblyAI auth key
assembly_AI_auth_key = assemblyAI_auth_key
upload_response = None
# Function to fetch video IDs from a YouTube playlist
def get_all_videos_in_playlist(api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_video_ids = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50  # Maximum allowed by API
        )
        response = request.execute()
        for item in response['items']:
            all_video_ids.append(item['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    return all_video_ids

# Function to fetch video details from YouTube API
def get_video_details(api_key, video_ids):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(video_ids)
    )
    response = request.execute()
    video_details = []
    for item in response['items']:
        title = item['snippet']['title']
        duration = item['contentDetails']['duration']
        video_details.append({
            "title": title,
            "duration": duration
        })
    return video_details

# Function to download and save audio
def save_audio(link):
    SAVE_PATH = os.path.abspath("./audio_files")
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    try:
        yt = YouTube(link)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    audio_stream = yt.streams.get_audio_only()
    filename = yt.title
    for char in [' ', '-']:
        filename = filename.replace(char, '_')
    temp_webm_file_path = os.path.join(SAVE_PATH, f"{filename}.webm")
    try:
        audio_stream.download(output_path=SAVE_PATH, filename=f"{filename}.webm")
    except Exception as e:
        print(f"An error occurred while downloading: {e}")
        return None
    mp3_file_path = os.path.join(SAVE_PATH, f"{filename}.mp3")
    try:
        subprocess.run([
            'ffmpeg',
            '-i', temp_webm_file_path,
            mp3_file_path
        ])
    except Exception as e:
        print(f"An error occurred while converting: {e}")
        return None
    print("Task Completed!")
    return mp3_file_path

# Streamlit App
st.title('Earnings Call Transcription & Sentiment Analysis')

api_key = yt_auth_key
playlist_id = st.text_input("Enter the Playlist ID")

# Define the CHUNK_SIZE and read_file function once
CHUNK_SIZE = 5242880

def read_file(filename):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(CHUNK_SIZE)
            if not data:
                break
            yield data


# Initialize an empty dictionary to keep track of all saved audio file locations
saved_audio_locations = {}
upload_response = None  # Initialize upload_response here

# AssemblyAI endpoints and headers
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
headers_auth_only = {'authorization': assembly_AI_auth_key}
headers = {
    "authorization": assembly_AI_auth_key,
    "content-type": "application/json"
}

if api_key and playlist_id:
    all_video_ids = get_all_videos_in_playlist(api_key, playlist_id)
    video_details = get_video_details(api_key, all_video_ids)
    
    selected_videos = {}
    for i, (video, video_id) in enumerate(zip(video_details, all_video_ids), 1):
        selected_videos[video_id] = st.checkbox(f"Title: {video['title']}, Duration: {video['duration']}")
    
    if st.button("Download and Transcribe Selected Videos"):
        for video_id, selected in selected_videos.items():
            if selected:
                link = f"https://www.youtube.com/watch?v={video_id}"
                save_location = save_audio(link)
                if save_location:
                    saved_audio_locations[video_id] = save_location
        
        # Here is where you'll fill upload_response with the actual value
        for video_id, save_location in saved_audio_locations.items():
            upload_response = requests.post(
                upload_endpoint,
                headers=headers_auth_only, data=read_file(save_location)
            )



# Streamlit App
st.title('Earnings Call Transcription & Sentiment Analysis')

api_key = yt_auth_key
playlist_id = st.text_input("Enter the Playlist ID", key='playlist_id_input')

saved_audio_locations = {}

if api_key and playlist_id:
    all_video_ids = get_all_videos_in_playlist(api_key, playlist_id)
    video_details = get_video_details(api_key, all_video_ids)
    
    selected_videos = {}
    for i, (video, video_id) in enumerate(zip(video_details, all_video_ids), 1):
        selected_videos[video_id] = st.checkbox(f"Title: {video['title']}, Duration: {video['duration']}", key=f"checkbox_{i}")
    
    if st.button("Download and Transcribe Selected Videos", key='download_button'):
        for video_id, selected in selected_videos.items():
            if selected:
                link = f"https://www.youtube.com/watch?v={video_id}"
                save_location = save_audio(link)
                if save_location:
                    saved_audio_locations[video_id] = save_location
        
        # Upload audio to AssemblyAI after all audio files have been downloaded
        for video_id, save_location in saved_audio_locations.items():
            upload_response = requests.post(
                upload_endpoint,
                headers=headers_auth_only, data=read_file(save_location)
            )
audio_url = upload_response.json()['upload_url']
print('Uploaded to', audio_url)



## Start transcription job of audio file
data = {
	'audio_url': audio_url,
	'sentiment_analysis': 'True',
}

transcript_response = requests.post(transcript_endpoint, json=data, headers=headers)
print(transcript_response)

transcript_id = transcript_response.json()['id']
polling_endpoint = transcript_endpoint + "/" + transcript_id

print("Transcribing at", polling_endpoint)


def add_bullet_points(text):
    sentence_enders = ['.', '!', '?']
    sentences = []
    start = 0

    for i, char in enumerate(text):
        if char in sentence_enders:
            sentence = text[start:i+1].strip()
            sentences.append(f"• {sentence}")
            start = i+1

    bullet_point_text = '\n'.join(sentences)
    return bullet_point_text



## Waiting for transcription to be done
status = 'submitted'
while status != 'completed':
	print('Processing...not ready yet')
	sleep(3)
	polling_response = requests.get(polling_endpoint, headers=headers)
	transcript = polling_response.json()['text']
	status = polling_response.json()['status']
	
# Add bullet points to the transcript
bullet_point_transcript = add_bullet_points(transcript)

# Display transcript
print('creating transcript')
st.sidebar.header('Transcript of the earnings call')
st.sidebar.markdown(bullet_point_transcript)


print(json.dumps(polling_response.json(), indent=4, sort_keys=True))



## Sentiment analysis response	
sar = polling_response.json()['sentiment_analysis_results']

## Save to a dataframe for ease of visualization
sen_df = pd.DataFrame(sar)
print(sen_df.head())




## Visualizations
st.markdown("### Number of sentences: " + str(sen_df.shape[0]))


grouped = pd.DataFrame(sen_df['sentiment'].value_counts()).reset_index()
grouped.columns = ['sentiment','count']
print(grouped)


col1, col2 = st.columns(2)


# Display number of positive, negative and neutral sentiments
fig = px.bar(grouped, x='sentiment', y='count', color='sentiment', color_discrete_map={"NEGATIVE":"firebrick","NEUTRAL":"navajowhite","POSITIVE":"darkgreen"})

fig.update_layout(
	showlegend=False,
    autosize=False,
    width=400,
    height=500,
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    )
)

col1.plotly_chart(fig)


## Display sentiment score
pos_perc = grouped[grouped['sentiment']=='POSITIVE']['count'].iloc[0]*100/sen_df.shape[0]
neg_perc = grouped[grouped['sentiment']=='NEGATIVE']['count'].iloc[0]*100/sen_df.shape[0]
neu_perc = grouped[grouped['sentiment']=='NEUTRAL']['count'].iloc[0]*100/sen_df.shape[0]

sentiment_score = neu_perc+pos_perc-neg_perc

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode = "delta",
    value = sentiment_score,
    domain = {'row': 1, 'column': 1}))

fig.update_layout(
	template = {'data' : {'indicator': [{
        'title': {'text': "Sentiment score"},
        'mode' : "number+delta+gauge",
        'delta' : {'reference': 50}}]
                         }},
    autosize=False,
    width=400,
    height=500,
    margin=dict(
        l=20,
        r=50,
        b=50,
        pad=4
    )
)

col2.plotly_chart(fig)

## Display negative sentence locations
fig = px.scatter(sar, y='sentiment', color='sentiment', size='confidence', hover_data=['text'], color_discrete_map={"NEGATIVE":"firebrick","NEUTRAL":"navajowhite","POSITIVE":"darkgreen"})


fig.update_layout(
	showlegend=False,
    autosize=False,
    width=800,
    height=300,
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    )
)

st.plotly_chart(fig)


# Create DataFrame from sentiment_analysis_results
df = pd.DataFrame(sar)

# Create a new DataFrame with the specific columns you want
# "index" is assumed to be the index in the DataFrame
# "column" can be any other column you might want from the original DataFrame
# For this example, I am assuming "confidence" could be the "column"

new_df = df[['sentiment', 'text', 'confidence']].copy()
new_df.reset_index(inplace=True)
new_df.rename(columns={'confidence': 'column'}, inplace=True)

# Sort DataFrame by 'index'
sorted_df = new_df.sort_values(by='index')

# Display sorted DataFrame
print(sorted_df)

st.write(sorted_df)



if __name__ == '__main__':
    print("This will run when the script is run.")