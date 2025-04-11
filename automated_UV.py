# demonstrating using requests library to drive Keen's Web API

import os
import requests
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('keen.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))
logging.basicConfig(filename='keen.log', level=logging.INFO)

def get_key():
    # Get the Keen API key from a local file secret.txt
    with open('secret.txt') as f:
        return f.read().strip()



def get_keen_data(api_key, event_collection, timeframe):
    # Set up the request headers
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    # Set up the request parameters
    params = {
        'event_collection': event_collection,
        'timeframe': timeframe
    }

    # Make the request to Keen's Web API
    response = requests.get(f'https://br7ls2mdjpzkmchaeuwlp6hf540zimfq.lambda-url.us-east-1.on.aws/', headers=headers, params=params)

    if response.status_code == 200:
        logger.info(f'Successfully retrieved data from Keen: {response.json()}')
    else:
        logger.error(f'Failed to retrieve data from Keen: {response.text}')



if __name__ == '__main__':
    # endpoint: https://br7ls2mdjpzkmchaeuwlp6hf540zimfq.lambda-url.us-east-1.on.aws/
    get_keen_data(get_key(), 'LA-data', 'last_24_hours')