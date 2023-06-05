# A web crawler to download files from SGX

This is a web crawler to download files (WEBPXTICK_DT-\*.zip, TickData_structure.dat, TC_\*.txt, TC_structure.dat) from [Singapore Exchange](https://www.sgx.com/research-education/derivatives).

## Features:
- Command line options and config files support
- Download historical files and today's file based on user instructions
- Logging implementation for better visibility
- Auto-recover/Resume failed tasks in case of temporary network or server issues. Manual intervention required for authentication or specific errors.

## Setup

- Python version: 3.10.4
- Install dependencies: `pip install -r requirements.txt`


## Usage

    usage: crawl.py [-h] [-d DATE] [-l] [--latest] [--cron CRON] [-rcv]

    SGX File Downloader. By default, it will schedule a daily cron job to download or recover files at 8 AM.

    options:
    -h, --help            show this help message and exit
    -d DATE, --date DATE  Specify the date to download files in the format: YYYYMMDD, e.g., 20221231.
    -l, --list            List the five previous days.
    --latest              Download the latest files.
    --cron CRON           Schedule a cron job for downloading the latest files and recovering failed dates. 
                          Specify the cron schedule in the format: "HH:MM", e.g., "08:00".
    -rcv, --recover       Recover all failed dates.


## Examples

- To download files for a specific date, run: `python crawl.py -d 20221231`
- To schedule a cron job for automatic download and recovery, run: `python crawl.py --cron "00:00"`
- Failed dates are stored in `failed_dates.txt`. To recover/resume the download, run: `python crawl.py -rcv`

## Notice

- Files are downloaded to the data directory, and logs are written to log_file.log.
- Due to a one-day trade date delay, downloading today's data will always fail.
- For some earliest dates, the file names are different (`TC_structure.dat` is named `TickData_structure.dat`, `WEBPXTICK_DT-\*.zip` is named `\*\_web.tic`, `TC_\*.txt` is named `\*\_web.atic1`). This code does not handle these cases.
- Sometimes, some files may be missing from the website.
