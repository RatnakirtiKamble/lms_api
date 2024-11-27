from flask import Flask
from utils.core_utils import attempt_login, get_subjects, get_subject_materials, get_download_link

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/get_subjects')
def get_subjects_route():
    subjects = get_subjects(attempt_login("rat.kam.rt22@dypatil.edu", "Ratna@1234"))

    return subjects
    
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
