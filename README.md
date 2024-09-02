
# SSH Login Alert Script

This script monitors SSH login attempts on a Linux system, specifically by parsing /var/log/auth.log. It sends alerts to a Discord webhook whenever a successful or failed SSH login attempt is detected from an IP address not listed in a whitelist.

<img src="https://github.com/user-attachments/assets/ddbf41c6-6a0b-4934-8bcf-a841c184c4d5" width="400px">


## Features

- **Monitors SSH login attempts:** Detects both successful and failed login attempts.
- **IP Whitelisting:** Alerts are only triggered for IP addresses not listed in the whitelist.txt file.
- **IP Geolocation:** Provides the country and city of the login attempt (using the ipinfo.io API).
- **Timezone Configuration:** Supports custom timezones for accurate timestamping.
- **Runs as a Service:** Can be set up to run as a persistent system service.


## Requirements

- Python 3.x
- **'requests'** library
- **'pytz'** library

### Install Required Python Libraries

You can install the necessary Python libraries using pip:

```bash
pip install requests pytz
```
## Setup

**1. Clone this repository**

```bash
  git clone https://github.com/nplachkov/ssh-alerts.git
  cd ssh-alerts

```

**2. Configure the Discord Webhook**

```bash
  echo "https://your-discord-webhook-url" > discord-webhook.txt
```

**3. Configure the Whitelist**


Add your whitelisted IPs/Subnets to the whitelist.txt file in the project directory. Those will be ignored by the alert system. Each entry should be on a new line.

```bash
  echo "192.168.1.150" >> whitelist.txt
  echo "192.168.0.0/24" >> whitelist.txt
```

- CIDR Notation: You can specify entire subnets using CIDR notation (e.g., 192.168.0.0/24).
- Single IPs: You can whitelist individual IP addresses (e.g., 10.0.0.1).


**4. Running the Script**

  
You can run the script directly using Python:

```bash
  python3 ssh-alerts.py
```

**5. Running as a Systemd Service**

  
To run the script as a service:

**5.1. Create the Service File**
```bash
sudo nano /etc/systemd/system/ssh-alerts.service
```

Add the following content:
```bash
[Unit]
Description=SSH Alerts Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 [PATH_TO_THE_SCRIPT]/ssh-alerts/ssh-alerts.py
WorkingDirectory=[PATH_TO_THE_SCRIPT]/ssh-alerts/ssh-alerts.py
Restart=on-failure
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

**5.2. Start and Enable the Service**

Reload systemd to recognize the new service:

```bash
sudo systemctl daemon-reload
```

Start the service:

```bash
sudo systemctl start ssh-alerts.service
```

Enable the service to start on boot:

```bash
sudo systemctl enable ssh-alert.service
```

**5.3. Check Service Status**

To check if the service is running:

```bash
sudo systemctl status ssh-alert.service
```
## Customization

### Timezone Configuration

The script includes a **'TIMEZONE'** setting that you can adjust to match your local timezone. The current setting is for **'Europe/Sofia'** (UTC+2 or UTC+3 during DST). You can change this in the script:

```bash
TIMEZONE = 'Europe/Sofia'
```

To use a different timezone, refer to the list of timezones supported by the pytz library: [List of Pytz Timezones.](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)



## License

This project is licensed under the MIT License. See the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.

