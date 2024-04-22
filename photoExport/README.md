# Photo Insights Application

## Overview

This Flask application allows users to upload photos, from which it extracts EXIF metadata and utilizes AWS Rekognition for object detection. Additionally, it leverages the OpenAI API to generate interesting facts and captions based on the photo's content and geographical metadata. The app also supports dynamic caption regeneration.

## Features

- **Photo Upload**: Users can upload photos in JPEG format.
- **Metadata Extraction**: Extracts and displays metadata such as GPS coordinates and camera details from the photos.
- **Location-based Insights**: Converts GPS coordinates to a readable address and provides interesting facts about the location using OpenAI's language model.
- **Object Detection**: Uses AWS Rekognition to identify objects and scenes in the photo.
- **Caption Generation**: Generates captions for uploaded photos based on detected objects, landmarks, and location insights.
- **Dynamic Caption Regeneration**: Allows users to regenerate captions with new or adjusted input parameters.

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```
2. Install the required Python packages:
  ```pip install -r requirements.txt```

3. Set up the necessary environment variables in a .env file:
   ```bash
  OPENAI_API_KEY=[Your OpenAI API Key]
  AWS_ACCESS_KEY_ID=[Your AWS Access Key ID]
  AWS_SECRET_ACCESS_KEY=[Your AWS Secret Access Key]
  app_secret_key=[Your Flask App Secret Key]```
  
4. Run the application:
  ```python app.py```

5. Usage
Navigate to http://localhost:5000 in your web browser to access the application. Upload a photo through the interface and view the extracted data, generated insights, and captions displayed on the photo's dedicated page.
