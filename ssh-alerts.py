import os
import re
import json
import requests
import time
import pytz
from datetime import datetime
from ipaddress import ip_address, ip_network

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WEBHOOK_FILE = os.path.join(SCRIPT_DIR, 'discord-webhook.txt')
LOG_FILE_PATH = '/var/log/auth.log'
WHITELIST_FILE = os.path.join(SCRIPT_DIR, 'whitelist.txt')
GEOLOC_API_URL = 'http://ipinfo.io/{}/json'  # IP geolocation service
TIMEZONE = 'Europe/Sofia'  # Set your timezone here

def get_webhook_url():
    if not os.path.isfile(WEBHOOK_FILE):
        raise FileNotFoundError(f"Webhook file not found: {WEBHOOK_FILE}")
    with open(WEBHOOK_FILE, 'r') as f:
        webhook_url = f.read().strip()
    if not webhook_url:
        raise ValueError("Webhook URL is empty")
    return webhook_url

WEBHOOK = get_webhook_url()  # Define WEBHOOK globally

def load_whitelist():
    whitelist = []
    if os.path.isfile(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    whitelist.append(line)
    return whitelist

def is_ip_whitelisted(ip, whitelist):
    ip = ip_address(ip)
    for entry in whitelist:
        if '/' in entry:
            if ip in ip_network(entry, strict=False):
                return True
        else:
            if ip == ip_address(entry):
                return True
    return False

def get_ip_info(ip):
    try:
        response = requests.get(GEOLOC_API_URL.format(ip))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching IP info: {e}")
        return {}

def format_timestamp(timezone_str=TIMEZONE):
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)
    return now.strftime("%d/%m/%Y, %H:%M:%S")

def process_log_file(last_position, whitelist):
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            f.seek(last_position)
            lines = f.readlines()

            new_position = f.tell()

        for line in lines:
            # Debug: Print the log line to ensure correct parsing
            print(f"Processing line: {line.strip()}")

            if 'sshd' in line:
                if 'Accepted' in line:
                    # Update regex for successful logins based on provided log line
                    match = re.search(r'Accepted (publickey|password) for (\S+) from (\d+\.\d+\.\d+\.\d+) port \d+', line)
                    if match:
                        auth_type, username, ip_address = match.groups()
                        if not is_ip_whitelisted(ip_address, whitelist):
                            post_log(ip_address, username, "Successful Login Attempt")
                elif 'Connection closed' in line:
                    match = re.search(r'Connection closed by authenticating user (\S+) (\d+\.\d+\.\d+\.\d+) port \d+ \[preauth\]', line)
                    if match:
                        username, ip_address = match.groups()
                        if not is_ip_whitelisted(ip_address, whitelist):
                            post_log(ip_address, username, "Failed Login Attempt")

        return new_position

    except Exception as e:
        print(f"Error processing log file: {e}")
        return last_position

def post_log(ip, user, status):
    timestamp = format_timestamp()
    ip_info = get_ip_info(ip)
    country = ip_info.get('country', 'Unknown Country')
    city = ip_info.get('city', 'Unknown City')

    embed = {
        "title": f"SSH {status}",
        "description": (f"**User:** {user}\n"
                        f"**IP Address:** {ip}\n"
                        f"**Country:** {country}\n"
                        f"**City:** {city}\n"
                        f"**Timestamp:** {timestamp}"),
        "color": 16734296
    }
    
    payload = {"embeds": [embed]}
    
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(WEBHOOK, headers=headers, data=json.dumps(payload))
        if response.status_code != 204:
            print(f"Post Failed with code {response.status_code}")
    except Exception as e:
        print(f"Error posting to webhook: {e}")

def main():
    last_position = 0
    whitelist = load_whitelist()

    if os.path.isfile(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, 'r') as f:
                f.seek(0, os.SEEK_END)
                last_position = f.tell()
        except Exception as e:
            print(f"Error initializing file position: {e}")

    while True:
        last_position = process_log_file(last_position, whitelist)
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
