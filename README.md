# Job Post Request Script

This script reads job post data from a CSV file and sends POST requests to a specified API URL. The script can be configured using environment variables and command-line arguments.

## Prerequisites

- Python 3.7 or later
- `requests` library

Install the `requests` library if you haven't already:

```bash
pip install requests
```

## Configuration

Ensure you have a `config.py` file in the same directory as your script with the following variables defined:

```python
# config.py

API_URL = "https://your-api-url.com"
DEFAULT_CATEGORY = "test"
DEFAULT_COUNTRY = "gb"
CSV_FILE_PATH = "job_posts.csv"
```

## Environment Variables

Set the `SECRET_KEY` environment variable, which is used for authentication in API requests:

- On Unix-like systems (Linux, macOS):

    ```bash
    export SECRET_KEY="<your_secret_key_value>"
    ```

- On Windows:

    ```bash
    setx SECRET_KEY "<your_secret_key_value>"
    ```

## Usage

Run the script with the following command:

```bash
python script.py [options]
```

### Command-Line Options

- `-h`, `--help`: Show the help message and exit.
- `-c CATEGORY`, `--category CATEGORY`: Category for the job post (default: test).
- `-n COUNTRY`, `--country COUNTRY`: Country for the job post (default: gb).
- `-s SECRET_KEY`, `--secret-key SECRET_KEY`: Secret key for authentication.
- `-f CSV_FILE`, `--csv-file CSV_FILE`: Path to the CSV file (default: `job_posts.csv`).

### Example

```bash
python script.py --secret-key your_secret_key --category live --country us --csv-file my_job_posts.csv
```

## Logging

The script logs its actions to both the console and a log file named `job_posts.log`. Each log entry is followed by a horizontal rule for better readability.

## Error Handling

The script includes error handling for network requests and file operations. If an error occurs, it will be logged and printed to the console.

## Concurrency

The script uses a thread pool to concurrently send multiple requests, improving performance when processing a large number of job posts.

## CSV File Format

The CSV file should contain the following headers:

- `jobPostId`: Unique identifier for the job post.
- `url`: The URL for the job post.

Example CSV content:

```csv
jobPostId,url
12345,http://example.com/job/12345
67890,http://example.com/job/67890
```

## Github

This project can be found on [GitHub](https://github.com/crozuk/bulkJobMining).

## Author

Richard Crosby - [Website](https://richardcrosby.co.uk)
