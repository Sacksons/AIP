# utils.py (new)
import boto3
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

async def upload_to_s3(file: UploadFile, key: str):
    s3_client.upload_fileobj(file.file, BUCKET_NAME, key)
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

def get_s3_url(key: str):
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"