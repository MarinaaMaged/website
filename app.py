from flask import Flask, jsonify,render_template,Response, send_from_directory
import requests
import os
from flask_cors import CORS
import cv2

app = Flask(__name__)
camera=cv2.VideoCapture(0)

CORS(app)
firebase_url = "https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/.json"

def generate_frames():
    while True:
        success, frame = camera.read()  # Read the frame from the camera
        if not success:
            break
        else:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  # Convert to bytes
            
            # Yield the frame with the proper format for multipart streaming
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

@app.route('/')
def index():
     return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'live.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
