# config.py
import os

# API endpoint URL
API_URL = 'https://services.automation.cloud/v1/recruitment/job-posts/mine/'

# Default values for category and country
DEFAULT_CATEGORY = 'test'
DEFAULT_COUNTRY = 'gb'

# Maximum response body length to log
MAX_RESPONSE_BODY_LENGTH = 500

# Retrieve the SECRET_KEY from the environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')