from flask import Flask, jsonify,render_template,Response, send_from_directory
import requests
import os
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import threading

app = Flask(__name__)
cred = credentials.Certificate("D:\C IoT\website\website\iot-workout-tracker-firebase-adminsdk-v1zcl-dc66c26ef7.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/'  
})

cap = None  # Global variable for the video capture object

# Define global variables to control the video stream
streaming = False
stream_thread = None

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
left_counter=0
left_stage=None
right_counter=0
right_stage=None

left_counter_ref = db.reference('left_counter')
right_counter_ref = db.reference('right_counter')
left_stage_ref = db.reference('left_stage')
right_stage_ref = db.reference('right_stage')
cap=cv2.VideoCapture(0)

CORS(app)
firebase_url = "https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/.json"

def calculate_angle(a,b,c): #first med final
    a=np.array(a) 
    b=np.array(b)
    c=np.array(c)

    radians = np.arctan2(c[1]-b[1],c[0]-b[0]) - np.arctan2(a[1]-b[1],a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle>180.0:
        angle=360-angle
    return angle

def generate_frames():
    global left_counter, right_counter, left_stage, right_stage

    with mp_pose.Pose(min_detection_confidence =0.5,min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret,frame = cap.read()

            #to detect 
            image=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            image.flags.writeable = False 
    #detect
            results = pose.process(image)
            # recoloring
            image.flags.writeable = True
            image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)

            #extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                #coordinates
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow =[landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist= [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                left_angle= calculate_angle(shoulder,elbow,wrist)

                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

                
                #visualize angle
                cv2.putText(image,str(left_angle),
                            tuple(np.multiply(elbow,[640,480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA
                )

                cv2.putText(image, str(right_angle),
                            tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

                #curl counter logic
                if left_angle > 160:
                    left_stage = "down"
                if left_angle < 30 and left_stage == "down":
                    left_stage = "up"
                    left_counter += 1
                    print(f"Left Counter: {left_counter}")

                    left_counter_ref.set(left_counter)
                    left_stage_ref.set(left_stage)

                # Curl counter logic for right arm
                if right_angle > 160:
                    right_stage = "down"
                if right_angle < 30 and right_stage == "down":
                    right_stage = "up"
                    right_counter += 1
                    print(f"Right Counter: {right_counter}")

                    right_counter_ref.set(right_counter)
                    right_stage_ref.set(right_stage)

            # print(landmarks)
            except:
                pass

            #status
            cv2.rectangle(image, (0, 0), (600, 100), (245, 117, 16), -1)

            # Left arm status
            cv2.putText(image, 'LEFT REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, str(left_counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Left Stage', (110, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, left_stage, (110, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Right arm status
            cv2.putText(image, 'RIGHT REPS', (320, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, str(right_counter), (320, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Right Stage', (420, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, right_stage, (420, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Render pose landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))
                # Encode the image as a JPEG
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()

            # Use yield to return a stream of images
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
                    },
                    "left_counter": data["left_counter"],
                    "left_stage": data["left_stage"],
                    "right_counter": data["right_counter"],
                    "right_stage": data["right_stage"]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/start_stream', methods=['GET'])
def start_stream():
    global streaming, stream_thread, cap
    if not streaming:
        streaming = True
        cap = cv2.VideoCapture(0)
        stream_thread = threading.Thread(target=generate_frames)
        stream_thread.start()
    return jsonify({'message': 'Stream started'})

@app.route('/stop_stream', methods=['GET'])
def stop_stream():
    global streaming, cap
    if streaming:
        streaming = False
        cap.release()
    return jsonify({'message': 'Stream stopped'})

@app.route('/live.css')
def send_css():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'live.css')

@app.route('/')
def index():
     return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'live.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
