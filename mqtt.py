import eventlet
eventlet.monkey_patch()
from flask import Flask, jsonify, render_template, Response, send_from_directory
from flask_cors import CORS
import paho.mqtt.client as paho
from paho import mqtt
import os
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate( "iot-workout-tracker-firebase-adminsdk-v1zcl-883936917f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/'
})

app = Flask(__name__)
mqtt_thread_instance = None
stop_event = Event()
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5500")
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    client.subscribe("sensor/humidity", qos=0)
    client.subscribe("fitness/profile/age", qos=0)

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == "fitness/profile/age":
        socketio.emit('profile_data', {'message': msg.payload.decode()})
    elif msg.topic == "sensor/humidity":
        socketio.emit('new_data', {'message': msg.payload.decode()})  # Emit message to all connected Socket.IO clients

# Initialize the MQTT Client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("RomaMagdy", "Password2912")
client.connect("6e3d738d12824ef5afc1d35354f43032.s1.eu.hivemq.cloud", 8883)

def mqtt_thread():
    client.loop_forever()  # This will run in a separate thread

@app.route('/')
def index():
    return "MQTT Flask-SocketIO Server Running!"

if __name__ == "__main__":
    # Start the MQTT client in a separate thread
    mqtt_thread_instance = Thread(target=mqtt_thread)
    mqtt_thread_instance.start()

    # Run the Flask-SocketIO server
    socketio.run(app, host='127.0.0.1', port=5001, debug=True, use_reloader=False)
