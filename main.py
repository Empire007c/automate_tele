import json
import os
import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initial settings for coco
coco_initial_storage = 1000
coco_initial_multitap =  4
coco_storage_incre = 500
coco_multitap_incre = 1

# Path to the JSON file
JSON_FILE = 'users.json'

# Load the data from the JSON file
def load_users():
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, 'r') as f:
            data = f.read().strip()
            if data == "":
                return []
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# Save the user data to the JSON file
def save_users(users):
    with open(JSON_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Find user by id in the list of users
def find_user_by_id(users, userid):
    for user in users:
        if user["id"] == userid:
            return user
    return None
    
@app.route('/update', methods=['GET'])
# Function to update the coco delay by reducing 60 continuously every 60 seconds
def update_coco_delay():
    try:
        while True:
            users = load_users()
            for user in users:
                if user['coco']['delay'] is not None and isinstance(user['coco']['delay'], (int, float)):
                    user['coco']['delay'] -= 60*10

                    # If delay is less than or equal to 0, set it to True
                    if user['coco']['delay'] <= 0:
                        user['coco']['delay'] = True

            # Write the updated data back to the file
            save_users(users)
            print(users)

            # Wait for 60 seconds before the next update
            #time.sleep(60)
            return "updated"
    except Exception as e:
        print(f"Error: {e}")

@app.route('/<userid>', methods=['GET'])
def check_user(userid):
    users = load_users()

    # Find if the user exists in the list
    user = find_user_by_id(users, userid)

    # If user not registered, add them to the list
    if not user:
        new_user = {  
            "id": userid,
            "coco": {"delay":None,"touches":None},
            "sd": {"delay":None,"touches":None},
        }
        users.append(new_user)
        save_users(users)
        user = new_user

    return jsonify(user)

@app.route('/<userid>/<data>', methods=['GET'])
def user_update(userid, data):
    users = load_users()

    # Find user
    user = find_user_by_id(users, userid)

    # Check if user exists
    if not user:
        return jsonify({"error": f"User with id {userid} not found."}), 404

    # Parse the data
    pairs = data.split(", ")
    data = {k.strip(): v.strip() for k, v in (pair.split(": ") for pair in pairs)}

    # Extract values and calculate touches and delay
    coco_ml = int(data["coco_ml"][2:])  # Extract the level number
    coco_stl = int(data["coco_stl"][2:])  # Extract the level number

    coco_touches = round((((coco_stl-1) * coco_storage_incre) + coco_initial_storage) / ((coco_ml-1) + coco_initial_multitap))
    coco_delay = (((coco_stl-1) * coco_storage_incre) + coco_initial_storage)

    # Update the user data
    user["coco"]["delay"] = coco_delay
    user["coco"]["touches"] = coco_touches

    # Save updated users list
    save_users(users)

    return jsonify(user)

@app.route('/clear/users_data', methods=['GET'])
def clear_users():
    # Overwrite the file with an empty list to clear all users
    with open(JSON_FILE, 'w') as f:
        json.dump([], f, indent=4)
    
    return jsonify({"message": "All users have been cleared."}), 200

@app.route('/get/users_data', methods=['GET'])
def get_users():
    # Load users
    users = load_users()
    return jsonify(users)

if __name__ == '__main__':
    

    # Run the Flask app
    app.run(debug=False)
