import boto3
import os
from os.path import basename
import re
import logging

logging.basicConfig(level=logging.DEBUG)

class S3CameraRecordingsInterface(object):

    EXTRA_ARGS = {
        'ContentType': 'video/mp4',
        'StorageClass': 'STANDARD'
    }

    def __init__(self):
        self.__s3_client = boto3.client('s3')

    def __parse_key(self, file_path):
        pattern = re.compile('(.*?)_(.*?)_(.*?)_(.*?)_()')
        file_name = basename(file_path)
        match = pattern.match(file_name)

        if match is None:
            return 

        camera_name = match.group(1)
        year = match.group(2)
        month = match.group(3)
        day = match.group(4)
        file_name = file_name

        return f'{camera_name}/{year}/{month}/{day}/{file_name}'


    def store_recording(self, file_path, bucket):
        key  = self.__parse_key(file_path)

        if key is None:
           logging.warn('Passed file name does not meet the format of <camera_name>_<year>_<month>_<day>__<hour>_<minute>_<second>.mp4. Skipping Storage')
        else:
            logging.info(f'Storing file at "{file_path}" to bucket "{bucket}" as "{key}"')
            self.__s3_client.upload_file(
                Filename=file_path, 
                Bucket=bucket, 
                Key=key,
                ExtraArgs=self.EXTRA_ARGS
            )
