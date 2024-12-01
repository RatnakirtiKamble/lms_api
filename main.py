from flask import Flask, session, jsonify, request, send_from_directory, abort
from utils.core_utils import attempt_login, get_subjects, get_subject_materials, get_download_link
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'hriddhi'  # Use a secure key!


username = "hri.hal.rt22@dypatil.edu"
password = "mili#36912"
cookie = attempt_login(username, password)
subjects = get_subjects(cookie)

def refresh_cookie():
    global cookie
    cookie = attempt_login(username, password)
    print("Cookie refreshed successfully!")

@app.route('/')
def home():
    try: 
        get_materials()
    except:
        refresh_cookie()
        get_materials()




@app.route('/materials', methods=['GET'])
def get_materials():

    link = request.args.get('link')

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
    print('yes')
    print(subjects)
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
