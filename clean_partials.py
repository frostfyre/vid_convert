# go through all files recursively from a given folder, check their size, and if they are smaller than a given threshold, delete them

import os
import sys
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('cleanup.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))
logging.basicConfig(filename='cleanup.log', level=logging.INFO)

def clean_partials(folder, threshold=22000):
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) < threshold and file_path.endswith('.avif'):
                logger.info(f'Deleting {file_path}')
                os.remove(file_path)
            else:
                logger.debug(f'File {file_path} is larger than threshold')

def report_partials(folder, threshold=22000):
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) < threshold and file_path.endswith('.avif'):
                logger.info(f'Found partial file: {file_path}')
            else:
                logger.debug(f'File {file_path} is larger than threshold')

if __name__ == '__main__':
    # use args to determine whether to report or cleanse
    if len(sys.argv) < 2:
        logger.error('Please provide a folder to check')
        sys.exit(1)
    folder = sys.argv[1]
    if len(sys.argv) == 3:
        threshold = int(sys.argv[2])
    else:
        threshold = 22000
    if 'preview' in sys.argv:
        report_partials(folder, threshold)
    else:
        clean_partials(folder, threshold)
    logger.info('Done')
