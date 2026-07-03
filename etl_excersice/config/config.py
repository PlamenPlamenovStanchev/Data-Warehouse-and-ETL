import os
from dotenv import load_dotenv

load_dotenv()

#AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FOLDER_NAME = os.getenv("FOLDER_NAME")

#Database Configuration
USER = os.getenv("USER")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")