from flask import Flask, session, jsonify, request
from utils.core_utils import attempt_login, get_subjects, get_subject_materials

app = Flask(__name__)
app.secret_key = 'hriddhi'  # Use a secure key!

@app.route('/materials', methods=['GET'])
def get_materials():
    if 'cookie' not in session:
        return jsonify({"message": "User not logged in"}), 401
    
    user_cookie = session['cookie']

    # Extract the subject link from query parameters
    subject_link = request.args.get('link')
    if not subject_link:
        return jsonify({"message": "Subject link is required"}), 400

    try:
        materials = get_subject_materials(subject_link, user_cookie)
        return jsonify(materials), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    # Replace these with actual request data (e.g., from a login form)
    username = "rat.kam.rt22@dypatil.edu"
    password = "Ratna@1234"
    session_cookie = attempt_login(username, password)
    if session_cookie:
        session['cookie'] = session_cookie  # Store cookie in the session
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login failed"}), 401

@app.route('/get_subjects', methods=['GET'])
def get_subjects_route():
    if 'cookie' not in session:
        return jsonify({"message": "User not logged in"}), 401
    
    user_cookie = session['cookie']
    try:
        subjects = get_subjects(user_cookie)
        return jsonify(subjects), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
