import requests
import json

url = "http://localhost:5000/predict_side_effects"

import os

# Get path relative to the script
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "test_data.json")

with open(data_path, "r") as f:
    data = json.load(f)

headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())
