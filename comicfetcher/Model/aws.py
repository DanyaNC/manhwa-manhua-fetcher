import logging
import boto3
from botocore.exceptions import ClientError
import os

# As per https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

s3_client = boto3.client('s3')

BUCKET_NAME = 'comicimages'
AWS_SERVER = 'us-east-2'

def upload_to_s3(file_name, bucket=BUCKET_NAME, object_name=None):
    """Upload image to the S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_s3_url(file_name):
    object_name = os.path.basename(file_name)
    return f'https://{BUCKET_NAME}.s3.{AWS_SERVER}.amazonaws.com/{object_name}'


def is_uploaded_s3(file_name: str) -> bool:
    object_name = os.path.basename(file_name)
    try:
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=object_name)
    except ClientError as e:
        return False
    return True

if __name__ == "__main__":
    pass
