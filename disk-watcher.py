import time
import sys
from os import path
import logging
import paho.mqtt.client as mqtt
from configparser import ConfigParser
import shutil
import socket
import sdnotify

LOGGING_FORMAT = '%(name)s %(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)


config = ConfigParser()
HERE = path.dirname(path.realpath(__file__))
config.read(path.join(HERE, 'disk-watcher.conf'))
logger = logging.getLogger(name='disk-watcher')
logger.setLevel(config['default'].get('loglevel', 'INFO').upper())

systemd = sdnotify.SystemdNotifier()

MQTT_BROKER = config['mqtt.broker']
HOST = MQTT_BROKER['host']
PORT = int(MQTT_BROKER['port'])
KEEPALIVE = int(MQTT_BROKER['keepalive'])

PUBLISHING = config['publishing']
BASE_TOPIC = PUBLISHING['topic_base'] + "/" + socket.gethostname()
FREQUENCY = int(PUBLISHING['frequency'])

DISKS = list(config['filesystems'].values())

logging.info('Monitoring the following file systems:')
for disk in DISKS:
    logging.info(disk)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))


MqttClient = mqtt.Client()
MqttClient.on_connect = on_connect


def publisher():
    logger.info("Starting to read free disk space")
    systemd.notify("READY=1")
    while True:
        for disk in DISKS:
            total, used, free = shutil.disk_usage(disk)
            if (disk == '/'):
                disk = '/root'
            path = "/disk" + disk
            logger.debug("Path: {}, disk: {}, total: {}, used: {}, free: {}".format(
                path, disk, total, used, free
            ))
            MqttClient.connect(HOST, PORT, KEEPALIVE)
            MqttClient.publish(BASE_TOPIC + path + "/total_gb", (total // (2**30)))
            MqttClient.publish(BASE_TOPIC + path + "/used_gb", (used // (2**30)))
            MqttClient.publish(BASE_TOPIC + path + "/free_gb", (free // (2**30)))
            MqttClient.publish(BASE_TOPIC + path + "/used_pct", (used/total * 100))
            MqttClient.disconnect()
        systemd.notify("WATCHDOG=1")
        time.sleep(FREQUENCY)


def main():
    try:
        publisher()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Quitting.")
        systemd.notify("STOPPING=1")
        sys.exit(0)
    except Exception:
        logger.exception("Unhandled exception during execution.", exc_info=True)
        systemd.notify("STATUS=An exception occured.\nERRNO=1")
        sys.exit(1)


if __name__ == '__main__':
    main()
