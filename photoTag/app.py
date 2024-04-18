# app.py

import wikipedia
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import exif
import pandas as pd
import requests
from openai import OpenAI
import cv2
import numpy as np

client = OpenAI(api_key='')


app = Flask(__name__)

def load_yolo_model():
    net = cv2.dnn.readNet("yolo/yolov3.weights", "yolo/yolov3.cfg")
    classes = []
    with open("yolo/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes

# Configure the upload directory
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the file is present in the request
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Check if the file has a valid filename
        if file.filename == '':
            return redirect(request.url)
        # Check if the file extension is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read metadata from the photo
            with open(file_path, 'rb') as f:
                metadata = exif.Image(f)

            # Convert metadata to a dictionary
            metadata_dict = {}
            for attr in dir(metadata):
                if not attr.startswith('_'):
                    try:
                        metadata_dict[attr] = getattr(metadata, attr)
                    except (AttributeError, NotImplementedError):
                        # Skip the attribute if it raises an AttributeError or NotImplementedError
                        pass

            # Create a DataFrame from the metadata dictionary
            df = pd.DataFrame.from_dict(
                metadata_dict, orient='index', columns=['Value'])

            # Keep only the specified columns
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
            df = df.loc[columns_to_keep]

        # Get the latitude, longitude, and timestamp from the metadata
        # Get the latitude, longitude, timestamp, and camera make from the metadata
        latitude = df.loc['gps_latitude', 'Value']
        latitude_ref = df.loc['gps_latitude_ref', 'Value']
        longitude = df.loc['gps_longitude', 'Value']
        longitude_ref = df.loc['gps_longitude_ref', 'Value']
        datestamp = df.loc['gps_datestamp', 'Value']
        lens_make = df.loc['lens_make', 'Value']

        # Convert latitude and longitude to decimal degrees
        lat_deg, lat_min, lat_sec = latitude
        lon_deg, lon_min, lon_sec = longitude
        lat_decimal = lat_deg + (lat_min / 60) + (lat_sec / 3600)
        lon_decimal = lon_deg + (lon_min / 60) + (lon_sec / 3600)
        if latitude_ref == 'S':
            lat_decimal = -lat_decimal
        if longitude_ref == 'W':
            lon_decimal = -lon_decimal

        # Perform reverse geocoding to get the location
        url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat_decimal}&lon={lon_decimal}'
        response = requests.get(url)
        location_data = response.json()
        location = location_data.get('display_name', 'Unknown Location')

        try:
            location_summary = wikipedia.summary(location, sentences=2)
        except wikipedia.exceptions.DisambiguationError as e:
            location_summary = wikipedia.summary(e.options[0], sentences=2)
        except wikipedia.exceptions.PageError:
            location_summary = "No information found."

        # Use the LLM to generate an interesting fact about the location

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that generates interesting facts or informative phrases about locations based on given information."
                },
                {
                    "role": "user",
                    "content": f"Based on the following information about {location}, generate an interesting fact or informative phrase:\n\n{location_summary}"
                }
            ],
            temperature=0.7,
            max_tokens=100,
            n=1,
            stop=None,
        )

        interesting_fact = response.choices[0].message.content.strip()

        # Format the timestamp
        timestamp = datestamp.replace(':', '-')

        # Perform object detection on the uploaded image
        net, classes = load_yolo_model()
        image = cv2.imread(file_path)
        height, width, _ = image.shape

        blob = cv2.dnn.blobFromImage(image, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers = net.getUnconnectedOutLayersNames()
        layer_outputs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        detected_objects = [classes[class_id] for class_id in class_ids]

        # ... (existing code for location, interesting fact, etc.)

        return render_template('upload.html', filename=filename, location=location, timestamp=timestamp,
                               lens_make=lens_make, interesting_fact=interesting_fact, detected_objects=detected_objects)

    return render_template('upload.html')


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == '__main__':
    app.run(debug=True)
