from googleapiclient.discovery import build
from google_config import auth_key
import streamlit as st
from pytube import YouTube
import os
import subprocess

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
st.title('YouTube Video Details')

api_key = auth_key
playlist_id = st.text_input("Enter the Playlist ID")

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
                save_audio(link)
