from flask import Flask, session, jsonify, request, send_from_directory, abort
from utils.core_utils import attempt_login, get_subjects, get_subject_materials, get_download_link
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = 'hriddhi'  # Use a secure key!


username = os.getenv("USERNAME")
password =  os.getenv("PASSWORD")
cookie = ""

print(username, password)

def refresh_cookie():
    global cookie
    cookie = attempt_login(username, password)
    print("Cookie refreshed successfully!")

@app.route('/')
def home():
    return "Hello world", 200




@app.route('/materials', methods=['GET'])
def get_materials():

    link = request.args.get('link')
    if cookie == "":
        refresh_cookie()
        
    if cookie:
        try:
            return get_subject_materials(link, cookie)
        except Exception as e:
            refresh_cookie()
            return get_subject_materials(link, cookie)
    
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
    
@app.route('/get_material', methods=['GET'])
def get_material():
    link = request.args.get('link')
    type = request.args.get('type')

    if cookie:
        content = get_download_link(link, type, cookie)
        return content
    

@app.route('/login', methods=['POST'])
def login():
    # Replace these with actual request data (e.g., from a login form)
    session_cookie = attempt_login(username, password)
    if session_cookie:
        session['cookie'] = session_cookie  # Store cookie in the session
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login failed"}), 401

@app.route('/get_subjects', methods=['GET'])
def get_subjects_route():
    subjects = get_subjects(cookie)
    print(subjects)
    if len(subjects) == 0:
        refresh_cookie()
        return jsonify(get_subjects(cookie)), 200
    return jsonify(subjects), 200
   
        

@app.route('/download/<filename>')
def download_file(filename):
    try:
        print(f"Attempting to serve file: {filename}")
        return send_from_directory('static/downloads', filename, as_attachment=True), 200
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return abort(404)
    except Exception as e:
        print(f"Error: {e}")
        return abort(500)
   
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
