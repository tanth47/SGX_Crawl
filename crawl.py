import requests
import os
import argparse
import sys
import schedule
import time
from utils import *

def download_latest_files():
    logger.info("Downloading latest files")
    # First, we get the latest key
    logger.info("Getting latest key")
    url = 'https://api3.sgx.com/infofeed/Apps?A=COW_Tickdownload_Content&B=TimeSalesData'
    try:
        response = requests.get(url)
    except Exception as e:
        logger.critical(e.__clas__.__name__)
        return
    if response.status_code == 200:
        data = response.json()
        latest_date = data['items'][0]['TC Data File'].split('.')[0].split('_')[1]
        logger.debug(f"Latest date: {latest_date}")
    else:
        logger.critical(f"Server error when get latest date - status code: {response.status_code}")
        return
    
    # Then, we download the files
    download_files_by_date(latest_date)

def list_5_days_past():
    logger.info("Listing 5 days past")
    url = 'https://api3.sgx.com/infofeed/Apps?A=COW_Tickdownload_Content&B=TimeSalesData'
    try:
        response = requests.get(url)
    except Exception as e:
        logger.critical(e.__clas__.__name__)
        return
    if response.status_code == 200:
        data = response.json()
        for key in data['items']:
            try:
                item_date = key['TC Data File'].split('.')[0].split('_')[1]
            except:
                continue
            logger.info(f"Key: {key['key']} for date: {item_date}")
    else:
        logger.critical(f"Server error when list 5 days past - status code: {response.status_code}")

def download_files_by_key(key: int) -> bool:
    logger.debug(f"Downloading files for key: {key}")
    files_types = ['WEBPXTICK_DT.zip', 'TickData_structure.dat', 'TC_structure.dat', 'TC.txt']
    url = f"https://links.sgx.com/1.0.0/derivatives-historical/{key}/"
    date = ''
    for file_type in files_types:
        try:
            response = requests.get(url + file_type)
        except Exception as e:
            logger.critical(e.__clas__.__name__)
            return False
        if response.status_code == 200:
            if file_type == 'WEBPXTICK_DT.zip':
                try:
                    date = response.headers['Content-Disposition'].split('=')[1].split('.')[0].split('-')[1]
                except:
                    logger.warning("No record found for this key")
                    return True
                if not os.path.exists(f"data/{date}"):
                    os.makedirs(f"data/{date}")
            with open(f"data/{date}/{file_type}", 'wb') as file:
                file.write(response.content)
            logger.info(f"File {file_type} downloaded succesfully.")
        else:
            logger.critical(f"Server error when downloading files {file_type} - status code: {response.status_code}")
            return False
    logger.info("Download completed.")
    return True

def find_key_by_date(date: str) -> int:
    # First, check whether the date is valid
    if not is_valid_date(date):
        logger.error("Invalid date")
        return None
    logger.debug(f"Finding key for date: {date}")
    # Now, we find the key for the date
    logger.debug("Checking whether the date is in 5 days past")
    url = 'https://api3.sgx.com/infofeed/Apps?A=COW_Tickdownload_Content&B=TimeSalesData'
    try:
        response = requests.get(url)
    except Exception as e:
        logger.critical(e.__class__.__name__)
        return -1
    is_older_than_5_days = False
    latest_key = 0
    if response.status_code == 200:
        data = response.json()
        for key in data['items']:
            try:
                item_date = key['TC Data File'].split('.')[0].split('_')[1]
            except:
                continue
            is_older_than_5_days = (item_date > date)
            latest_key = max(latest_key, int(key['key']))
            if item_date == date:
                logger.debug("Key found!")
                logger.debug(f"Key: {key['key']} for date: {item_date}")
                return int(key['key'])
        logger.debug("Date not found in 5 days past")
    else:
        logger.debug("Error when get key in 5 days past - status code: {response.status_code}")
        return -1


    # If the date is not found in 5 days past, we look up further, 
    logger.debug("Looking up further")

    # Date is newer than the latest date in 5 days past, so we can't find the key
    if not is_older_than_5_days:
        logger.debug("Cannot find the key for this date")
        return None
    
    # using binary search for speed up, because there are many days is not available, so we can't simply minus by key
    # Left is set to 2755 because for the key les than 2755, the file format is different, we can fix this code if needed
    Left = 2755
    Right = latest_key
    check = False
    while Left <= Right:
        Mid = (Left + Right) // 2
        logger.debug(f"Checking key: {Mid}, Left: {Left}, Right: {Right}")
        try:
            response = requests.get(f"https://links.sgx.com/1.0.0/derivatives-historical/{Mid}/WEBPXTICK_DT.zip")
        except Exception as e:
            logger.critical(e.__clas__.__name__)
            return -1
        if response.status_code == 200:
            item_date = response.headers['Content-Disposition'].split('=')[1].split('.')[0].split('-')[1]
            if item_date == date:
                logger.debug("Key found!")
                logger.debug(f"Key: {Mid} for date: {item_date}")
                check = True
                return Mid
            elif item_date < date:
                Left = Mid + 1
            else:
                Right = Mid - 1
    
    if not check:
        logger.debug("Cannot find the key for this date")
        return None

def download_files_by_date(date: str) -> bool:
    # First, check whether the date is valid
    if not is_valid_date(date):
        logger.error("Invalid date")
        return True
    logger.info(f"Starting proces for date: {date}")
    failed_date_controller.add_date(date)
    # Now, we find the key for the date
    key = find_key_by_date(date)
    if key == -1:
        logger.critical(f'Download failed for date: {date}')
        return False
    elif key is not None:
        if not download_files_by_key(key):
            logger.critical(f'Download failed for date: {date}')
            return False
    else:
        logger.info("Cannot find data for this date")
    logger.info(f"Proces completed for date: {date}")
    failed_date_controller.remove_last_date()
    return True

def recover_failed_dates():
    logger.info("Recovering and resuming files for failed dates")
    failed_dates = failed_date_controller.get_all_failed_dates() # unique list
    new_failed_dates = []
    for date in failed_dates:
        if not download_files_by_date(date):
            new_failed_dates.append(date)
    failed_date_controller.set_failed_dates(new_failed_dates)
    logger.info("Recovering and resuming files for failed dates completed")

def download_and_recover_files():
    # First, download the files
    download_latest_files()

    # Second, recover and resume files for failed dates
    recover_failed_dates()

def schedule_job(cron_schedule: str):
    # Schedule job
    print(f"Schedule job with cron schedule: {cron_schedule}")
    print((lambda: str(datetime.now()))())
    schedule.every().day.at(cron_schedule).do(download_and_recover_files)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SGX File Downloader. By default, it will schedule a daily cron job to download or recover files at 8 AM.')
    parser.add_argument('-d', '--date', type=str, help='Specify the date to download files in the format: YYYYMMDD, e.g., 20221231.')
    parser.add_argument('-l', '--list', action='store_true', help='List the five previous days.')
    parser.add_argument('--latest', action='store_true', help='Download the latest files.')
    parser.add_argument('--cron', type=str, help='Schedule a cron job for downloading the latest files and recovering failed dates. Specify the cron schedule in the format: "HH:MM", e.g., "08:00".')
    parser.add_argument('-rcv', '--recover', action='store_true', help='Recover all failed dates.')
    args = parser.parse_args()

    logger = logger_config()
    failed_date_controller = FailedDateController()
    if args.date:
        download_files_by_date(args.date)
    if args.list:
        list_5_days_past()
    if args.latest:
        download_latest_files()
    if args.recover:
        recover_failed_dates()
    if args.cron or len(sys.argv) == 1:
        schedule_job(args.cron or "08:00")
        while True:
            schedule.run_pending()
            time.sleep(1)