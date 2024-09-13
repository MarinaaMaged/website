from flask import Flask, jsonify, render_template, Response, send_from_directory, request
import requests
import os
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import threading
import paho.mqtt.client as paho
from paho import mqtt

app = Flask(__name__)
cred = credentials.Certificate("flutter-project-eea51-firebase-adminsdk-ngomz-9234c88a9e.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://flutter-844ee-default-rtdb.firebaseio.com' })

cap = None  # Global variable for the video capture object

# Define global variables to control the video stream
streaming = False
stream_thread = None
stream_lock = threading.Lock()  # Lock to ensure safe threading
stop_event = threading.Event()  # Event to signal thread to stop

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
left_counter = 0
left_stage = None
right_counter = 0
right_stage = None

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})
firebase_url = "https://flutter-844ee-default-rtdb.firebaseio.com/.json"

def calculate_angle(a, b, c):
    a = np.array(a) 
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

def generate_frames():
    global left_counter, right_counter, left_stage, right_stage, streaming, cap

    cap = cv2.VideoCapture(0)  # Ensure cap is initialized here
    if not cap.isOpened():
        return  # Exit if unable to access the camera

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while not stop_event.is_set():  # Check if stop event is set
            ret, frame = cap.read()
            if not ret:
                break

            # Processing frame
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Detect pose
            results = pose.process(image)

            # Recoloring and landmark processing
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                left_angle = calculate_angle(shoulder, elbow, wrist)

                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

                # Visualize angles
                cv2.putText(image, str(left_angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.putText(image, str(right_angle),
                            tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Curl counter logic
                if left_angle > 160:
                    left_stage = "down"
                if left_angle < 30 and left_stage == "down":
                    left_stage = "up"
                    left_counter += 1


                if right_angle > 160:
                    right_stage = "down"
                if right_angle < 30 and right_stage == "down":
                    right_stage = "up"
                    right_counter += 1


            except:
                pass

            # Status information on image
            cv2.rectangle(image, (0, 0), (600, 100), (245, 117, 16), -1)

            cv2.putText(image, 'LEFT REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, str(left_counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Left Stage', (110, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, left_stage, (110, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(image, 'RIGHT REPS', (320, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, str(right_counter), (320, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Right Stage', (420, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, right_stage, (420, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()  # Ensure camera is released when done
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Make a GET request to Firebase to retrieve all data
        response = requests.get(firebase_url)
        data = response.json()

        # Ensure the expected data fields exist
        if "Sensor" in data and "calc" in data:
            result = {
                "calc":{
                    "waterIntake": data["calc"]["waterIntake"],
                    "EE": data["calc"]["EE"],
                    "MHR": data["calc"]["MHR"],
                    "intensity": data["calc"]["intensity"],
                     "kcalPerHour": data["calc"]["kcalPerHour"]

                    }
                ,
                "Sensor": {
                    "heartRate": data["Sensor"]["heartRate"],
                    "temperature": data["Sensor"]["temperature"],
                    "spO2": data["Sensor"]["spO2"],   # Add spO2 if needed
                    "humidity": data["Sensor"]["humidity"] # Add humidity if needed
                },
                "Input":{
                    "age": data["Input"]["age"],
                    "weight": data["Input"]["weight"],
                    "name":  data["Input"]["name"],
                    "goals":  data["Input"]["goals"]
                    },
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/start_stream', methods=['GET'])
def start_stream():
    global streaming, stream_thread, cap
    with stream_lock:
        if not streaming:
            streaming = True
            stop_event.clear()  # Clear the stop event before starting
            stream_thread = threading.Thread(target=generate_frames)
            stream_thread.start()
    return jsonify({'message': 'Stream started'})

@app.route('/stop_stream', methods=['GET'])
def stop_stream():
    global streaming, stream_thread
    with stream_lock:
        if streaming:
            stop_event.set()  # Signal the thread to stop
            streaming = False
            if stream_thread is not None:
                stream_thread.join()  # Wait for the thread to terminate
    return jsonify({'message': 'Stream stopped'})



@app.route('/live.css')
def send_css():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'live.css')

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'live.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/publish_profile', methods=['POST'])
def publish_profile():
    profile_data = request.json
    name = profile_data.get('name', 'Unknown')
    weight = profile_data.get('weight', 'Unknown')
    age = profile_data.get('age', 'Unknown')
    goals = profile_data.get('goals', 'Unknown')

    # Publish to MQTT
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set("RomaMagdy", "Password2912")
    try:
        client.connect("6e3d738d12824ef5afc1d35354f43032.s1.eu.hivemq.cloud", 8883)

        message = f"Name: {name}, Weight: {weight}, Age: {age}, Goals: {goals}"
        result = client.publish("fitness/profile", message, qos=0)

        if result.rc != 0:
            return jsonify({"status": "error", "mqtt_error_code": result.rc})

    except Exception as e:
        return jsonify({"status": "error", "mqtt_error": str(e)})

    finally:
        client.disconnect()

   
    try:
        ref = db.reference('Input')
        ref.set({
            'name': name,
            'weight': weight,
            'age': age,
            'goals': goals
        })
        return jsonify({"status": "success", "message": "Profile updated in Firebase and published to MQTT"})
    
    except Exception as e:
        return jsonify({"status": "error", "firebase_error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
