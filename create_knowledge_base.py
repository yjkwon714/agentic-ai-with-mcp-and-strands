import boto3
import io
import logging
import os
import requests
import time
import uuid
import zipfile

from knowledge_base import BedrockKnowledgeBase
from tqdm import tqdm
from urllib.parse import urlparse


logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

session = boto3.session.Session()
region = os.getenv('AWS_REGION', session.region_name)
if region:
    print(f'Region: {region}')
else:
    print("Cannot determine AWS region from `AWS_REGION` environment variable or from `boto3.session.Session().region_name`")
    raise

s3_client = boto3.client('s3', region)
bedrock_agent_client = boto3.client('bedrock-agent', region)
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region)


def download_file(url):
    destination = os.path.basename(urlparse(url).path)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        file_size = int(response.headers.get('content-length', 0))

        with open(destination, 'wb') as file, tqdm(
            desc=destination,
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def extract_zip_file(zip_path):
    destination = '.'
    try:
        with zipfile.ZipFile(zip_path, 'r') as f:
            file_list = f.namelist()
            total_files = len(file_list)
            print(f"Extracting {total_files} files from {zip_path}")
            for file in tqdm(file_list, desc="Extracting"):
                f.extract(file, destination)

        print(f"Successfully extracted {total_files} files")
        return True
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file")
        return False
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return False

def create_s3_bucket_with_random_suffix(prefix):
    random_suffix = str(uuid.uuid4())[:8]
    bucket_name = f"{prefix.lower()}-{random_suffix.lower()}"
    try:
        if region == "us-east-1":
            # For us-east-1, we don't specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
            # For other regions, we need to specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )

        print(f"Successfully created bucket: {bucket_name}")

        # Wait for the bucket to be available
        waiter = s3_client.get_waiter('bucket_exists')
        waiter.wait(Bucket=bucket_name)
        return bucket_name

    except Exception as e:
        print(f"Error creating bucket: {e}")
        return None

def upload_directory(path, bucket_name):
    for root,dirs,files in os.walk(path):
        for file in files:
            file_to_upload = os.path.join(root,file)
            basename = os.path.basename(file_to_upload)
            if basename == ".DS_Store":
                continue
            print(f"uploading file {file_to_upload} to {bucket_name}")
            s3_client.upload_file(file_to_upload,bucket_name,file)

def create_n_sync_bedrock_knowledge_base(name, description, s3_bucket):
    knowledge_base = BedrockKnowledgeBase(
        kb_name=name,
        kb_description=description,
        data_bucket_name=s3_bucket,
        embedding_model = "amazon.titan-embed-text-v2:0"
    )
    time.sleep(30)
    knowledge_base.start_ingestion_job()
    return knowledge_base.get_knowledge_base_id()

def main():
    download_file("https://d2qrbbbqnxtln.cloudfront.net/pets-kb-files.zip")
    extract_zip_file("pets-kb-files.zip")
    s3_bucket = create_s3_bucket_with_random_suffix("bedrock-kb-bucket")
    print(f"Created S3 bucket: {s3_bucket}")
    upload_directory("pets-kb-files", s3_bucket)

    # Create Bedrock KnowledgeBase
    random_suffix = str(uuid.uuid4())[:8]
    knowledge_base_id = create_n_sync_bedrock_knowledge_base(
        name = f'pets-kb-{random_suffix}',
        description = "Pets Knowledge Base on cats and dogs",
        s3_bucket = s3_bucket
    )
    print(f'Created Bedrock Knowledge Base with ID: {knowledge_base_id}')

if __name__ == '__main__':
    main()
