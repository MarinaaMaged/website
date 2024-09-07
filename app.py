from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
firebase_url = "https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/.json"

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

if __name__ == '__main__':
    app.run(debug=True)
