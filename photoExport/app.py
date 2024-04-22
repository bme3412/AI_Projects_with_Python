import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import exif
from PIL import Image
from io import BytesIO
import pandas as pd
import requests
from openai import OpenAI
import boto3
from botocore.exceptions import NoCredentialsError
load_dotenv()

# Access your environment variable
api_key = os.getenv('OPENAI_API_KEY')
app_secret_key = os.getenv('app_secret_key')
rekognition = boto3.client('rekognition')
client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.secret_key = app_secret_key


ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return redirect(request.url)

    photo = request.files['photo']
    if photo.filename == '':
        return redirect(request.url)

    if photo and allowed_file(photo.filename):
        photo_data = photo.read()
        photo_stream = BytesIO(photo_data)
        photo_stream.seek(0)

        # Save the uploaded photo
        filename = photo.filename
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(photo_path, 'wb') as file:
            file.write(photo_data)

        return redirect(url_for('display_photo', filename=filename))

    return redirect(request.url)


@app.route('/photos/<path:filename>')
def display_photo(filename):
    photo_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(photo_path, 'rb') as file:
            photo_data = file.read()

        session['photo_filename'] = filename

        # Read metadata from the photo
        metadata = exif.Image(photo_data)

        metadata_dict = {}
        for attr in dir(metadata):
            if not attr.startswith('_'):
                try:
                    metadata_dict[attr] = getattr(metadata, attr)
                except (AttributeError, NotImplementedError):
                    pass

        df = pd.DataFrame.from_dict(
            metadata_dict, orient='index', columns=['Value'])

        columns_to_keep = [
            'gps_altitude',
            'gps_datestamp',
            'gps_img_direction',
            'gps_latitude',
            'gps_latitude_ref',
            'gps_longitude',
            'gps_longitude_ref',
            'lens_make',
            'lens_model'
        ]

        missing_columns = [
            col for col in columns_to_keep if col not in df.index]

        location = None
        interesting_fact = None

        if not missing_columns:
            latitude = df.loc['gps_latitude', 'Value']
            latitude_ref = df.loc['gps_latitude_ref', 'Value']
            longitude = df.loc['gps_longitude', 'Value']
            longitude_ref = df.loc['gps_longitude_ref', 'Value']

            lat_deg, lat_min, lat_sec = latitude
            lon_deg, lon_min, lon_sec = longitude
            lat_decimal = lat_deg + (lat_min / 60) + (lat_sec / 3600)
            lon_decimal = lon_deg + (lon_min / 60) + (lon_sec / 3600)
            if latitude_ref == 'S':
                lat_decimal = -lat_decimal
            if longitude_ref == 'W':
                lon_decimal = -lon_decimal

            url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat_decimal}&lon={lon_decimal}'
            response = requests.get(url)
            location_data = response.json()

            # Extract the desired location components
            address = location_data.get('address', {})
            road = address.get('road', '')
            suburb = address.get('suburb', '')
            city = address.get('city', '')
            country = address.get('country', '')

            # Format the location string
            location = f"{road}, {suburb}, {city}, {country}"

            # Generate interesting fact using LLM
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates interesting facts or informative phrases about locations based on given information."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the location {location}, generate an interesting fact or informative phrase."
                    }
                ],
                temperature=0.7,
                max_tokens=100,
                n=1,
                stop=None,
            )

            interesting_fact = response.choices[0].message.content.strip()

        if location is None:
            location = 'Unknown Location'

        # Use AWS Rekognition to analyze the photo
        try:
            response = rekognition.detect_labels(Image={'Bytes': photo_data})

            labels = [label['Name'] for label in response['Labels']]
            landmarks = [landmark['Name']
                         for landmark in response.get('Landmarks', [])]

            # Get the most confident label as the main subject
            if labels:
                main_subject = labels[0]
            else:
                main_subject = 'Unknown'

            # Generate a brief caption based on the detected objects and scenes
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates brief captions for images based on detected objects and scenes."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following detected objects and scenes, generate a brief caption for the image:\n\nDetected Objects and Scenes: {', '.join(labels)}"
                    }
                ],
                temperature=0.7,
                max_tokens=50,
                n=1,
                stop=None,
            )

            rekognition_caption = response.choices[0].message.content.strip()

            # Generate caption using LLM
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates captions for images based on location information, detected objects, and landmarks."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following information, generate a brief and punny caption (ho hashtags, but emohis are ok) suitable for a 36-year-old male Instagram user for the uploaded image:\n\nLocation: {location}\nInteresting Fact: {interesting_fact}\nDetected Objects: {', '.join(labels)}\nLandmarks: {', '.join(landmarks)}"
                    }
                ],
                temperature=0.7,
                max_tokens=100,
                n=1,
                stop=None,
            )

            caption = response.choices[0].message.content.strip()

            # Generate additional interesting fact using LLM
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates interesting facts based on location information, detected objects, and landmarks."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following information, generate an additional interesting fact or informative phrase related to the uploaded image:\n\nLocation: {location}\nInteresting Fact: {interesting_fact}\nDetected Objects: {', '.join(labels)}\nLandmarks: {', '.join(landmarks)}"
                    }
                ],
                temperature=0.7,
                max_tokens=100,
                n=1,
                stop=None,
            )

            additional_fact = response.choices[0].message.content.strip()

        except NoCredentialsError:
            rekognition_caption = "Caption generation failed due to missing AWS credentials."
            caption = "Caption generation failed due to missing AWS credentials."
            additional_fact = "Additional fact generation failed due to missing AWS credentials."
            main_subject = "Unknown"

        datestamp = df.loc['gps_datestamp',
                           'Value'] if 'gps_datestamp' in df.index else 'Unknown'
        lens_make = df.loc['lens_make',
                           'Value'] if 'lens_make' in df.index else 'Unknown'
        timestamp = datestamp.replace(
            ':', '-') if datestamp != 'Unknown' else 'Unknown'

        caption = request.args.get('caption', caption)
    
        return render_template('display_photo.html', filename=filename, location=location, timestamp=timestamp, lens_make=lens_make, interesting_fact=interesting_fact, caption=caption, additional_fact=additional_fact, rekognition_caption=rekognition_caption, main_subject=main_subject)

    except Exception as e:
        return str(e), 404


@app.route('/regenerate_caption/<path:filename>', methods=['POST'])
def regenerate_caption(filename):
    photo_filename = session.get('photo_filename')
    location = request.form.get('location')
    interesting_fact = request.form.get('interesting_fact')

    if photo_filename:
        try:
            response = rekognition.detect_labels(Image={'Bytes': photo_filename})

            labels = [label['Name'] for label in response['Labels']]
            landmarks = [landmark['Name']
                         for landmark in response.get('Landmarks', [])]

            # Generate caption using LLM
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates captions for images based on location information, detected objects, and landmarks."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following information, generate a brief and punny caption suitable for a 36-year-old male Instagram user for the uploaded image:\n\nLocation: {location}\nInteresting Fact: {interesting_fact}\nDetected Objects: {', '.join(labels)}\nLandmarks: {', '.join(landmarks)}"
                    }
                ],
                temperature=0.7,
                max_tokens=100,
                n=1,
                stop=None,
            )

            caption = response.choices[0].message.content.strip()

        except NoCredentialsError:
            caption = "Caption generation failed due to missing AWS credentials."

        return redirect(url_for('display_photo', filename=filename, caption=caption))

    else:
        return "No photo data found in the session.", 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
