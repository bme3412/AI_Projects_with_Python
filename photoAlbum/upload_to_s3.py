import os
from dotenv import load_dotenv
import boto3

# Load environment variables from .env file
load_dotenv()

# Configure AWS credentials and region
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

# Create an S3 client
s3 = boto3.client('s3', 
                  aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=aws_region)

# Specify the S3 bucket name
bucket_name = 'bme3412travelphotos'

# Specify the base path for the photos
base_path = '/Users/brendan/Desktop/photoExport'  # Adjust as needed

# Specify the folder names
folders = ['Argentina', 'Brazil', 'Chile']

# Iterate over the folders
for folder in folders:
    folder_path = os.path.join(base_path, folder)
    try:
        # Get the list of image files in the folder
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]

        # Upload each image file to S3
        for image_file in image_files:
            # Construct the S3 object key (path) for the image
            object_key = f'{folder}/{image_file}'
            
            # Path to the local image file
            local_image_path = os.path.join(folder_path, image_file)
            
            # Upload the image file to S3
            s3.upload_file(local_image_path, bucket_name, object_key)
            
            print(f'Uploaded {object_key} to S3')
    except FileNotFoundError:
        print(f"Error: The folder {folder_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

print('Image upload completed.')
