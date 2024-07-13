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

import config

# =============================================================================
# Setup logging
# =============================================================================
log_format = '%(asctime)s - %(levelname)s - %(message)s'
hr = '=' * 77
logging.basicConfig(level=logging.INFO, format=log_format)

# Create a file handler for logging to a text file
file_handler = logging.FileHandler('job_posts.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(f'{log_format}\n{hr}')
file_handler.setFormatter(file_formatter)
logging.getLogger().addHandler(file_handler)

def log_with_hr(logger_function, message: str):
    """Logs a message followed by a horizontal rule using a specified logger function."""
    logger_function(f"{message}\n{hr}")

# =============================================================================
# Configuration
# =============================================================================
url = config.API_URL  # API URL from the config module
default_category = config.DEFAULT_CATEGORY  # Default category
default_country = config.DEFAULT_COUNTRY    # Default country
max_response_body_length = 500              # Max length of response body to log

# =============================================================================
# Utility Functions
# =============================================================================

def encode_base64(string: str) -> str:
    base64_bytes = base64.b64encode(string.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def make_curl_request(job_post_id: str, job_url: str, category: str,
                      country: str, secret_key: str) -> None:
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
            log_message = (f"Request successful for job post ID: {job_post_id}\n"
                           f"Status Code: {response.status_code}\n"
                           f"Response Body: {response_body}")
            log_with_hr(logging.info, log_message)
            print(f"{log_message}\n{hr}")
        except requests_exceptions.HTTPError as e:
            if response.status_code == 401:
                log_message = f"Unauthorized access for job mining: {job_post_id}. Error: {e}"
            elif response.status_code == 404:
                log_message = f"Not found for job post ID: {job_post_id}. Error: {e}"
            else:
                log_message = f"HTTP error for job post ID: {job_post_id}. Status Code: {response.status_code}. Error: {e}"
            log_with_hr(logging.error, log_message)
            print(f"ERROR - {log_message}\n{hr}")
        except requests_exceptions.RequestException as e:
            log_message = f"Request failed for job post ID: {job_post_id}. Error: {e}"
            log_with_hr(logging.error, log_message)
            print(f"ERROR - {log_message}\n{hr}")

# =============================================================================
# Argument Parsing
# =============================================================================
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Send job post requests.')
    parser.add_argument('-c', '--category',
                        default=default_category,
                        help='Category for the job post (default: test)')
    parser.add_argument('-n', '--country',
                        default=default_country,
                        help='Country for the job post (default: gb)')
    parser.add_argument('-s', '--secret-key',
                        help='Secret key for authentication')
    parser.add_argument('-f', '--csv-file',
                        default=config.CSV_FILE_PATH,
                        help=f'Path to the CSV file (default: {config.CSV_FILE_PATH})')
    return parser.parse_args()

# =============================================================================
# Main Processing Function
# =============================================================================
def process_csv_rows(args: argparse.Namespace) -> None:
    logging.info("Starting job post requests processing")
    secret_key = os.environ.get('SECRET_KEY') or args.secret_key
    if not secret_key:
        log_message = "SECRET_KEY environment variable or --secret-key argument is not provided"
        log_with_hr(logging.error, log_message)
        print(f"ERROR - {log_message}\n{hr}")
        exit(1)

    try:
        start_time = time.time()
        total_posts = 0
        with open(args.csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            if 'jobPostId' not in reader.fieldnames or 'url' not in reader.fieldnames:
                raise ValueError("CSV does not contain required headers: 'jobPostId' and 'url'")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                job_posts_processed = set()

                for row in reader:
                    job_post_id = row['jobPostId']
                    job_url = row['url']
                    total_posts += 1

                    if job_post_id not in job_posts_processed:
                        futures.append(
                            executor.submit(make_curl_request, job_post_id,
                                            job_url, args.category,
                                            args.country, secret_key))
                        job_posts_processed.add(job_post_id)

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        log_message = f"Exception occurred for job post ID: {job_post_id}. Error: {e}"
                        log_with_hr(logging.error, log_message)
                        print(f"ERROR - {log_message}\n{hr}")

        duration = time.time() - start_time
        log_message = f"Total operation duration: {duration:.2f} seconds. Total job posts processed: {total_posts}"
        log_with_hr(logging.info, log_message)
        print(f"{log_message}\n{hr}")

    except FileNotFoundError:
        log_message = "CSV file not found. Please check the file path and try again."
        log_with_hr(logging.error, log_message)
        print(f"ERROR - {log_message}\n{hr}")
    except ValueError as e:
        log_message = f"Value error: {e}"
        log_with_hr(logging.error, log_message)
        print(f"ERROR - {log_message}\n{hr}")
    except Exception as e:
        log_message = f"An error occurred: {e}"
        log_with_hr(logging.error, log_message)
        print(f"ERROR - {log_message}\n{hr}")

    logging.info("Completed job post requests processing")

# =============================================================================
# Entry Point
# =============================================================================
if __name__ == "__main__":
    args = parse_arguments()
    process_csv_rows(args)