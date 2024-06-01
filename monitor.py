import os
import re
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def verify_filename_format(filename):
    base_part = os.path.splitext(os.path.basename(filename))[0]
    print("Base part for checking:", base_part)
    pattern = r"^(?:\d{1,5}|null)-(?:\d|null)-(?:[a-z]|null)-(?:\w+|null)$"
    return re.match(pattern, base_part) is not None

class S3Uploader(FileSystemEventHandler):
    def __init__(self, folder_path, bucket_name, region_name):
        self.folder_path = folder_path
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.log_file_path = os.path.join(folder_path, "wrong_convention_names.txt")

    def on_created(self, event):
        if not event.is_directory and verify_filename_format(event.src_path):
            if not self.is_file_in_bucket(event.src_path):
                self.upload_file_to_s3(event.src_path)
            else:
                print(f"File already exists in the bucket: {event.src_path}")
        else:
            self.log_wrong_format(event.src_path)
            print(f"Filename format is incorrect: {event.src_path}")

    def is_file_in_bucket(self, file_path):
        base_folder_name = os.path.basename(self.folder_path)
        relative_path = os.path.relpath(file_path, self.folder_path)
        s3_key = os.path.join(base_folder_name, relative_path.replace(os.sep, '/'))
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=s3_key)
        for item in response.get('Contents', []):
            if item['Key'] == s3_key:
                return True
        return False

    def upload_file_to_s3(self, file_path):
        base_folder_name = os.path.basename(self.folder_path)
        relative_path = os.path.relpath(file_path, self.folder_path)
        s3_key = os.path.join(base_folder_name, relative_path.replace(os.sep, '/'))
        try:
            with open(file_path, 'rb') as data:
                self.s3_client.upload_fileobj(data, self.bucket_name, s3_key)
                print(f"Uploaded {s3_key} to S3 bucket {self.bucket_name}")
        except Exception as e:
            print(f"Failed to upload {file_path} due to {str(e)}")

    def log_wrong_format(self, file_path):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(file_path + '\n')

def start_monitoring(folder_path, bucket_name, region_name):
    event_handler = S3Uploader(folder_path, bucket_name, region_name)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    print(f"Monitoring {folder_path} and uploading to {bucket_name}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Example usage
start_monitoring(r'C:\Users\ASUS\Desktop\Taleemabad\Job_Test_Task', 'fold-test', 'ap-south-1')
