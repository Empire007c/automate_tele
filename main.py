import json
import os
from flask import Flask, request, jsonify
from keep_alive import keep_alive  # Import the keep_alive function
# Call keep_alive() to keep the Replit instance running
keep_alive()
app = Flask(__name__)

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

    user = find_user_by_id(users, userid)

    if not user:
        new_user = {
            "id": userid,
            "coco": None,
            "sd": None,
            "sd1": None
        }
        users.append(new_user)
        save_users(users)
        user = new_user

    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
