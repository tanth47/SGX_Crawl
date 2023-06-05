import logging
from datetime import datetime
import requests
import urllib3

def is_valid_date(date_string: str):
    if len(date_string) != 8:
        return False
    try:
        datetime.strptime(date_string, "%Y%m%d")
        return True
    except ValueError:
        return False

def logger_config() -> logging.Logger:
    # Configure root logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Disable logging for requests and urllib3
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    # Create a handler
    handler = logging.FileHandler('log_file.log')
    handler.setLevel(logging.WARNING)


    # Create formatters for the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set formatters for the handlers
    handler.setFormatter(formatter)

    # Get the root logger
    logger = logging.getLogger()

    # Add the handlers to the logger
    logger.addHandler(handler)
    # logger.addHandler(console_handler)

    return logger

class FailedDateController:
    def add_date(self, date: str):
        with open('failed_dates.txt', 'a') as f:
            f.write(date + '\n')
    
    def remove_last_date(self):
        with open('failed_dates.txt', 'r') as f:
            lines = f.readlines()
        with open('failed_dates.txt', 'w') as f:
            f.writelines(lines[:-1])
    
    def get_all_failed_dates(self) -> list:
        with open('failed_dates.txt', 'r') as f:
            lines = f.readlines()
        return list(set([line.strip() for line in lines]))
    
    def set_failed_dates(self, dates: list):
        with open('failed_dates.txt', 'w') as f:
            f.writelines([date + '\n' for date in dates])
    