# s3-file-monitoring
File saved in system - it’s name is verified - uploaded to s3 bucket.

# S3 File Monitoring Script

## Overview
This script monitors a specified local directory for new files and automatically uploads them to an AWS S3 bucket if they meet the required filename format. It also checks if the file already exists in the bucket to prevent duplicates and logs incorrect file formats locally.

## Features
- **Real-time Monitoring**: Watches a local directory for new file creations.
- **S3 Upload**: Automatically uploads new files to a specified AWS S3 bucket.
- **Duplicate Check**: Ensures files aren't uploaded if they already exist in the bucket.
- **Format Validation**: Checks files against a specified naming convention and logs incorrect names.

## Prerequisites
Before you can run this script, you will need:
- Python 3.6 or higher.
- AWS account with S3 access.
- AWS CLI configured with access credentials (AWS Access Key ID and AWS Secret Access Key).

## Setup Instructions

### Install Python Dependencies
First, ensure that Python 3 is installed on your system. Then set up a virtual environment and install the required Python packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

## Configuration
Make sure your AWS credentials are set up properly. This can be done via environment variables, AWS credentials file, or AWS CLI:

```bash
set AWS_ACCESS_KEY_ID="your_access_key_id"
set AWS_SECRET_ACCESS_KEY="your_secret_access_key"
set AWS_DEFAULT_REGION="your_region"

Replace "your_access_key_id", "your_secret_access_key", and "your_region" with your actual AWS credentials.

## Running the Script
With the dependencies installed and the environment configured, you can start the script using:

```bash
python monitor.py

## Makefile Usage
For convenience, a 'Makefile' is included to handle setup and running:

```bash
make install  # Sets up the Python virtual environment and installs dependencies
make run      # Runs the script
