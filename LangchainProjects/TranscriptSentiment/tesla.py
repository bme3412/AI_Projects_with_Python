from googleapiclient.discovery import build
from google_config import yt_auth_key
import streamlit as st

# Your API Key (You can import this from another Python file if you want)
# api_key = YOUR_API_KEY  # Uncomment this line and replace YOUR_API_KEY
api_key = yt_auth_key

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

# Streamlit App
st.title('YouTube Video Details')

# Input for Playlist ID
playlist_id = st.text_input("Enter the Playlist ID")

if api_key and playlist_id:
    # Get all video IDs from the playlist
    all_video_ids = get_all_videos_in_playlist(api_key, playlist_id)

    # Get details of all videos in the playlist
    video_details = get_video_details(api_key, all_video_ids)

    for i, video in enumerate(video_details, 1):
        st.write(f"### Video {i}")
        st.write(f"**Title:** {video['title']}")
        st.write(f"**Duration:** {video['duration']}")
