# disk-watcher-mqtt

A very simple example of a service that periodically reports disk usage stats to an MQTT broker. I wrote this because I needed to keep an eye on the amount of free space on several Raspberry Pis around the house. I haven't written in Python in years, but I choose the language because it's available on all the Pis, even the Zero. So this is unlikely to be a good example of how to do this. I just needed it to work, not be elegant.

## Installation
```
sudo apt-get update
sudo apt install git python3-pip -y
git clone https://github.com/eamonnsullivan/disk-watcher-mqtt.git
cd disk-watcher-mqtt

# install the requirements
pip3 install -r requirements.txt

# edit the configuration
nano disk-watcher.conf
```
## Configuration

See `disk-watcher.conf`, set your broker, port, etc. You'll also want to set the topic_base (the first part of the topic) and the frequency (in seconds) of reporting.

## Set as a service

```
sudo ln -s /home/pi/disk-watcher/disk-watcher.service /etc/systemd/system/
sudo systemctl --system daemon-reload
sudo systemctl enable disk-watcher.service
sudo systemctl start disk-watcher.service
# wait a few seconds
sudo systemctl status disk-watcher.service
```
