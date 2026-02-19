# Updated coordinator.py

# Improvements: Added timeout handling and logging improvements.

import logging
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

class Coordinator:
    def __init__(self):
        self.timeout = 5  # Set timeout duration

    def fetch_data(self, url):
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise an error for bad status codes
            logging.info('Data fetched successfully from %s', url)
            return response.json()
        except requests.Timeout:
            logging.error('Request to %s timed out after %s seconds', url, self.timeout)
        except requests.RequestException as e:
            logging.error('Request failed: %s', e)

    # Add your existing methods here.