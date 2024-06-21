# Instructions:
#
# This script sends job post requests to a specific URL based on data read from a CSV file.
# Set the SECRET_KEY environment variable:
#    On Unix-like systems (Linux, macOS):
#      export SECRET_KEY="<your_secret_key_value>"
#    On Windows:
#      setx SECRET_KEY "<your_secret_key_value>"
#
# Usage:
#   python script.py [options]
#
# Options:
#   -h, --help            Show this help message and exit
#   -c CATEGORY, --category CATEGORY
#                         Category for the job post (default: test)
#   -n COUNTRY, --country COUNTRY
#                         Country for the job post (default: gb)
#   -s SECRET_KEY, --secret-key SECRET_KEY
#                         Secret key for authentication
#   -f CSV_FILE, --csv-file CSV_FILE
#                         Path to the CSV file (default: job_posts.csv)
#
# Example:
#   python script.py --secret-key your_secret_key --category draft --country us --csv-file my_job_posts.csv
#
# Note: If the SECRET_KEY environment variable is set, it will be used as the secret key.
#       Otherwise, the --secret-key argument must be provided.
# source env/bin/activate

# script.py
import config

import argparse
import base64
import concurrent.futures
import csv
import logging
import os
import time
from typing import Any, Dict

from requests import Session
from requests import exceptions as requests_exceptions

from dotenv import load_dotenv  # Import the load_dotenv function from the dotenv module

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler for logging to a text file
file_handler = logging.FileHandler('job_posts.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logging.getLogger().addHandler(file_handler)

# API URL
url = config.API_URL

# Default values for category and country
default_category = config.DEFAULT_CATEGORY
default_country = config.DEFAULT_COUNTRY

# Maximum response body length to log
max_response_body_length = 500

def encode_base64(string):
    base64_bytes = base64.b64encode(string.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def make_curl_request(job_post_id: str, job_url: str, category: str, country: str, secret_key: str) -> None:
    data: Dict[str, Any] = {
        "jobPostId": job_post_id,
        "url": job_url,
        "category": category,
        "country": country
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encode_base64(secret_key + ":")}'
    }

    with Session() as session:
        try:
            response = session.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_body = response.text[:max_response_body_length] + (
                '...' if len(response.text) > max_response_body_length else '')
            log_message = f"Request successful for job post ID: {job_post_id}\nStatus Code: {response.status_code}\nResponse Body: {response_body}"
            logging.info(log_message)
        except requests_exceptions.RequestException as e:
            log_message = f"Request failed for job post ID: {job_post_id}. Error: {e}"
            logging.error(log_message)
            print(f"ERROR - Request failed for job post ID: {job_post_id}. Error: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Send job post requests.')
    parser.add_argument('-c', '--category', default=default_category, help='Category for the job post (default: test)')
    parser.add_argument('-n', '--country', default=default_country, help='Country for the job post (default: gb)')
    parser.add_argument('-s', '--secret-key', help='Secret key for authentication')
    parser.add_argument('-f', '--csv-file', default='job_posts.csv', help='Path to the CSV file (default: job_posts.csv)')
    return parser.parse_args()

def process_csv_rows(args):
    # Get the SECRET_KEY from environment variable or command-line argument
    secret_key = os.environ.get('SECRET_KEY') or args.secret_key
    if not secret_key:
        logging.error("SECRET_KEY environment variable or --secret-key argument is not provided")
        exit(1)

    try:
        start_time = time.time()
        with open(args.csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            if 'jobPostId' not in reader.fieldnames or 'url' not in reader.fieldnames:
                raise ValueError("CSV does not contain required headers: 'jobPostId' and 'url'")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                job_posts_processed = set()  # Keep track of processed job post IDs

                for row in reader:
                    job_post_id = row['jobPostId']
                    job_url = row['url']

                    if job_post_id not in job_posts_processed:
                        futures.append(executor.submit(make_curl_request, job_post_id, job_url, args.category, args.country, secret_key))
                        job_posts_processed.add(job_post_id)

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        log_message = f"Exception occurred: {e}"
                        logging.error(log_message)

        end_time = time.time()
        duration = end_time - start_time
        log_message = f"Total operation duration: {duration:.2f} seconds\n---"
        logging.info(log_message)

    except FileNotFoundError:
        log_message = "CSV file not found. Please check the file path and try again."
        logging.error(log_message)
    except ValueError as e:
        log_message = f"Value error: {e}"
        logging.error(log_message)
    except Exception as e:
        log_message = f"An error occurred: {e}"
        logging.error(log_message)

# Parse command-line arguments
args = parse_arguments()

# Process CSV rows with parallelization
process_csv_rows(args)
