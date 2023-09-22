from pytube import YouTube
import os
import subprocess

def save_audio(link):
    # The path where you want to save the downloaded MP3
    SAVE_PATH = os.path.abspath("./audio_files")  # Save in the directory

    try:
        # Create a YouTube object
        yt = YouTube(link)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # Get the audio stream that has the best quality
    audio_stream = yt.streams.get_audio_only()

    # You can optionally set the filename for the downloaded video
    filename = yt.title

    # Replace characters in filename that could be problematic
    for char in [' ', '-']:
        filename = filename.replace(char, '_')

    # Generate a temporary file name for the WebM conversion
    temp_webm_file_path = os.path.join(SAVE_PATH, f"{filename}.webm")

    # Download the audio stream to the temporary file
    try:
        print(f"Downloading to {temp_webm_file_path}")
        audio_stream.download(output_path=SAVE_PATH, filename=f"{filename}.webm")
    except Exception as e:
        print(f"An error occurred while downloading: {e}")
        return None

    # Generate the mp3 file path
    mp3_file_path = os.path.join(SAVE_PATH, f"{filename}.mp3")

    # Convert the WebM file to MP3 using ffmpeg
    try:
        print(f"Converting {temp_webm_file_path} to {mp3_file_path}")
        subprocess.run([
            'ffmpeg',
            '-i', temp_webm_file_path,
            mp3_file_path
        ])
    except Exception as e:
        print(f"An error occurred while converting: {e}")
        return None

    # Delete the temporary WebM file if you want to
    # os.remove(temp_webm_file_path)

    print("Task Completed!")
    return mp3_file_path

# Example usage
link = "https://www.youtube.com/watch?v=k9hPBaFSkag"
save_audio(link)
