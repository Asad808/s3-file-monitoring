import os
import re
import boto3
import sys
import ctypes  # Import ctypes for displaying error message
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def verify_filename_format(filename):
    base_part = os.path.splitext(os.path.basename(filename))[0]
    print("Base part for checking:", base_part)
    pattern = r"^(?:\d{1,5})-(?:[1-5]|prep)-(?:[abcd]|null)-(?:math|english|urdu)$"
    if re.match(pattern, base_part):
        if "null" in base_part:
            return 'null_detected'
        return True
    return False

class S3Uploader(FileSystemEventHandler):
    def __init__(self, folder_path, bucket_name, aws_access_key_id, aws_secret_access_key, region_name):
        self.folder_path = folder_path
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.log_file_path = os.path.join(folder_path, "wrong_convention_names.txt")

    def upload_existing_files(self):
        for subdir, dirs, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(subdir, file)
                if "wrong_convention_names" not in file:
                    self.handle_file_upload(file_path)

    def on_created(self, event):
        if not event.is_directory and "wrong_convention_names" not in event.src_path:
            self.handle_file_upload(event.src_path)

    def handle_file_upload(self, file_path):
        if "wrong_convention_names" in file_path:
            return  # Skip uploading this file
        format_result = verify_filename_format(file_path)
        if format_result != True:
            self.log_wrong_format(file_path)
            ctypes.windll.user32.MessageBoxW(0, f"Incorrect file naming: {file_path}", "Error", 1)
            print(f"Stopping due to incorrect file naming: {file_path}")
            sys.exit(1)  # Exit the script
        if self.is_file_in_bucket(file_path):
            print(f"File already exists in the bucket and will be deleted: {file_path}")
            os.remove(file_path)  # Delete the file if it already exists in the bucket
        else:
            self.upload_file_to_s3(file_path)

    def is_file_in_bucket(self, file_path):
        base_folder_name = os.path.basename(self.folder_path)
        relative_path = os.path.relpath(file_path, self.folder_path)
        s3_key = os.path.join(base_folder_name, relative_path.replace(os.sep, '/'))
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=s3_key)
        return 'Contents' in response and any(item['Key'] == s3_key for item in response['Contents'])

    def upload_file_to_s3(self, file_path):
        base_folder_name = os.path.basename(self.folder_path)
        relative_path = os.path.relpath(file_path, self.folder_path)
        s3_key = os.path.join(base_folder_name, relative_path.replace(os.sep, '/'))
        try:
            with open(file_path, 'rb') as data:
                self.s3_client.upload_fileobj(data, self.bucket_name, s3_key)
                print(f"Uploaded {s3_key} to S3 bucket {self.bucket_name}")
                os.remove(file_path)  # Delete the file after successful upload
        except Exception as e:
            print(f"Failed to upload {file_path} due to {str(e)}")

    def log_wrong_format(self, file_path):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(file_path + '\n')

def start_monitoring(folder_path, bucket_name, aws_access_key_id, aws_secret_access_key, region_name):
    uploader = S3Uploader(folder_path, bucket_name, aws_access_key_id, aws_secret_access_key, region_name)
    uploader.upload_existing_files()  # Upload all existing files before starting monitoring
    observer = Observer()
    observer.schedule(uploader, folder_path, recursive=True)
    observer.start()
    print(f"Monitoring {folder_path} and uploading to {bucket_name}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

local_folder_path = r'your-local-folder-path-which-you-have-to-monitor'
bucket_name = 'your-bucket-name'
aws_access_key_id = 'AKIAWR******73CF'
aws_secret_access_key = 'e9**********TpebK'
region_name = 'ap-south-1'

start_monitoring(local_folder_path, bucket_name, aws_access_key_id, aws_secret_access_key, region_name)
