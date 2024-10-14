import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

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

    return jsonify(user,6878766)

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
    coco_delay = (coco_touches)

    # Update the user data
    user["coco"]["delay"] = coco_delay
    user["coco"]["touches"] = coco_touches

    # Save updated users list
    save_users(users)

    #return jsonify({"id": userid, "coco": {"delay": coco_delay, "touches": coco_touches}})
    return jsonify(user)


@app.route('/clear/users_data', methods=['GET'])
def clear_users():
    # Overwrite the file with an empty list to clear all users
    with open(JSON_FILE, 'w') as f:
        json.dump([], f, indent=4)
    
    return jsonify({"message": "All users have been cleared."}), 200
    
@app.route('/get/users_data', methods=['GET'])
def get_users():
    #load users
    users = load_users()
    return jsonify(users)
    


if __name__ == '__main__':
    app.run(debug=False)
