import random
import geocoder
import paho.mqtt.client as mqttclient
import time
import json
import requests

print("Xin chào ThingsBoard")


BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "u09iQUe98kUa7WqAFe0x"
API_KEY = "4256b3de394a56a86ee35e43af6f5c2e"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humid = 50
light_intensity = 100
counter = 0

longitude = 106.6297
latitude = 10.8231

# get the current location of ip address
cords = geocoder.ipinfo('me')
current_latitude = cords.latlng[0]
current_longitude = cords.latlng[1]
city = cords.city
data = requests.get(
    f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={API_KEY}"
)
current_temp = data.json().get('main')['temp']
current_humid = data.json().get('main')['humidity']

while True:
    collect_data = {'temperature': temp,
                    'humidity': humid,
                    'light': light_intensity,
                    'longitude': longitude,
                    'latitude': latitude,
                    'current_longitude': current_longitude,
                    'current_latitude': current_latitude,
                    'current_temp': current_temp,
                    'current_humid': current_humid
                    }
    temp += int(random.uniform(0, 10)) if (0 <= temp <= 80) else -2
    humid += int(random.uniform(0, 10)) if (0 <= humid <= 80) else -3
    light_intensity += int(random.uniform(0, 10)) if (0 <= light_intensity <= 200) else -5

    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(10)
