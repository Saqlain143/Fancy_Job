#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NUMBER_FILE = os.path.join(SCRIPT_DIR, 'number.txt')
SCRIPT_NAME = os.path.basename(__file__)

def read_number():
    try:
        with open(NUMBER_FILE, 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        logging.warning(f"{NUMBER_FILE} not found. Initializing to 0.")
        return 0
    except ValueError:
        logging.error(f"Invalid content in {NUMBER_FILE}. Initializing to 0.")
        return 0

def write_number(num):
    try:
        with open(NUMBER_FILE, 'w') as f:
            f.write(str(num))
        logging.info(f"Updated {NUMBER_FILE} with number: {num}")
    except Exception as e:
        logging.error(f"Failed to write to {NUMBER_FILE}: {e}")
        raise

def git_commit():
    try:
        subprocess.run(['git', 'add', 'number.txt'], check=True)
        date = datetime.now().strftime('%Y-%m-%d')
        commit_message = f"Update number: {date}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        logging.info("Changes committed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git commit failed: {e}")
        raise

def git_push():
    try:
        result = subprocess.run(['git', 'push'], check=True, capture_output=True, text=True)
        logging.info("Changes pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error pushing to GitHub: {e.stderr.strip()}")
        raise

def update_cron_with_random_time():
    try:
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)

        new_cron_command = f"{random_minute} {random_hour} * * * cd {SCRIPT_DIR} && python3 {os.path.join(SCRIPT_DIR, SCRIPT_NAME)}\n"

        cron_file = "/tmp/current_cron"
        os.system(f"crontab -l > {cron_file} 2>/dev/null || true")

        with open(cron_file, "r") as file:
            lines = file.readlines()

        with open(cron_file, "w") as file:
            for line in lines:
                if SCRIPT_NAME not in line:
                    file.write(line)
            file.write(new_cron_command)

        os.system(f"crontab {cron_file}")
        os.remove(cron_file)

        logging.info(f"Cron job updated to run at {random_hour}:{random_minute} daily.")
    except Exception as e:
        logging.error(f"Failed to update cron job: {e}")
        raise

def main():
    try:
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)

        git_commit()
        git_push()

        update_cron_with_random_time()

    except Exception as e:
        logging.critical(f"Script failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
