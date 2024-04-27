
# LlamaLens

The LlamaLens Caption Generator is a Flask web application that allows users to upload photos or select example photos, and generates captions and interesting facts based on the image content and metadata. It utilizes various APIs and libraries, including OpenAI's GPT-4, AWS Rekognition, and OpenStreetMap's Nominatim.

## Features

- Upload photos or select from example photos
- Extract metadata from uploaded photos (GPS location, timestamp, lens make, etc.)
- Detect objects, scenes, and landmarks in the photo using AWS Rekognition
- Generate captions and interesting facts based on the detected content and location using OpenAI's GPT-4
- Display the photo along with the generated captions, facts, and metadata
- Regenerate captions based on user input

## Installation

1. Clone the repository:
 ```
  git clone https://github.com/bme3412/LlamaLens.git
  cd LlamaLens
  ```
Copy code
2. Install the required dependencies:
 ```
  pip install -r requirements.txt
  ```
3. Set up the necessary environment variables:

- Create a `.env` file in the project root directory
- Add the following variables to the `.env` file:

  ```
  pip install -r requirements.txt
  ```

  Replace `your_openai_api_key` with your actual OpenAI API key and `your_app_secret_key` with a secret key for your Flask application.

4. Run the application:
```
  python app.py
  ```
Copy code
5. Open your web browser and navigate to `http://localhost:5000` to access the application.

## Usage

1. On the homepage, you can either upload a photo or select an example photo.
2. After selecting a photo, the application will process the image and display the generated captions, interesting facts, and metadata.
3. You can regenerate the caption by providing a new location or interesting fact and clicking the "Regenerate Caption" button.

## Project Structure

- `app.py`: The main Flask application file containing the routes and logic for handling photo uploads, caption generation, and display.
- `templates/`: Directory containing HTML templates for the application.
- `index.html`: The homepage template for uploading or selecting photos.
- `display_photo.html`: The template for displaying the photo along with captions, facts, and metadata.
- `uploads/`: Directory for storing uploaded photos.
- `static/`: Directory for storing example photos.

## Dependencies

- Flask: Web framework for building the application
- python-dotenv: Library for loading environment variables from a `.env` file
- exif: Library for extracting metadata from photos
- Pillow: Library for image processing
- pandas: Library for data manipulation and analysis
- requests: Library for making HTTP requests to external APIs
- openai: Library for interacting with OpenAI's APIs
- boto3: AWS SDK for Python, used for interacting with AWS Rekognition
