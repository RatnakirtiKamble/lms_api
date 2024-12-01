import requests
from bs4 import BeautifulSoup
from utils.site_parsing import parse_subjects, parse_attendance, parse_materials, parse_resource_link
import os
from werkzeug.utils import secure_filename


def attempt_login(username:str, password:str, session = None):
    """
        Creates a requests.session, makes a POST request to the LMS site, upon success, it writes
        the session cookies to the flask session object, to be used for future requests

            Parameters:
                username (str): A string of the student's official username
                password (str): A string of the student's password

            Returns:
                cookie_dict (dict): A dictionary containing the session cookies, as obtained by the Official site
    """
    try:
        with requests.session() as session:

            USER_DATA = {
                'username':username,
                'password':password
            }
            response = session.post(
                url="https://mydy.dypatil.edu/rait/login/index.php",
                data=USER_DATA,
                #stream=True  #set it to stream || to test ; non stream version seems to respond faster, need to investigate
            )

            #response.close() #instantly close the response, as we dont need the 80,000+ character response that contains irrelevant data (html, inline css, and javascript)

            # print(response.content) 
            #Successful login
            if response.status_code == 200:

                if response.headers['Content-Type'] == "text/html; charset=utf-8":


                    #convert to a dictionary
                    cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)

                    # return session.cookies, on a successful login
                    return cookie_dict

                else:
                    #incorrect credentials
                    return None

            #if login fails, return the response code
            return response.status_code
    except Exception as e:
        return None


def get_subjects(cookies) -> list[dict]:

    """
        Creates a session object, attaches the login cookies to this instance, and makes the fetch request for the subjects

        Parameters:
            cookies (dict): Cookies generated upon login action done on the official site

        Returns:
            subjects (list[dict]): Array of JSON Object/Python Dictionary containing subject details for logged in user:\n
                \t- Name
                \t- Instructor
                \t- Attendance
                \t- Link
                \t- Course ID
    """
    try:
        with requests.session() as session:

        #Insert the session cookies
            session.cookies = requests.utils.cookiejar_from_dict(cookie_dict=cookies)
            response = session.get('https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=myclasses')

            html_content = response.content
            #pass the html_content to a custom parsing block, that converts it into a neat json object 
            subjects = parse_subjects(html=html_content)
            # print(subjects)

            return subjects
    except Exception as e:
        return None


def get_subject_materials(link : str , cookies) -> list[dict]:
    """
        Fetches the given link, and returns a JSON containing links to the resource and titles


        Parameters:
            link (str): The subject link to be fetched and processed
            cookies (dict): Cookies generated upon login action done on the official site

        Returns:
            materials_json (list[dict]): List of course materials for a particular subject
    """

    with requests.session() as session:
        session.cookies = requests.utils.cookiejar_from_dict(cookie_dict=cookies)

        response = session.get(link)
        #get the string version of the response to pass to the parser
        response = response.content

        materials_json = parse_materials(response)


        return materials_json


def get_download_link(link : str, link_type, cookies):
    """
        Finds and returns a link to the .pdf, .pptx, or .docx resource for easy downloading.

        Parameters:
            link (str): The subject link to be fetched and processed
            cookies (dict): Cookies generated upon login action done on the official site

        Returns:
            An Object containing the following
            name: name of the file 
            link: link to the file requested
    """

    DOWNLOAD_FOLDER = 'static/downloads'
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


    # TODO: Implement a check to determine the kind of link (3-4 types exist I believe)
    with requests.session() as session:

        session.cookies = requests.utils.cookiejar_from_dict(cookie_dict=cookies)

        response = session.get(link)

        #parsing the response to extract the link

        extracted_link = parse_resource_link(response.content, link_type)

        content = None
        #Return object
        if (extracted_link != None):

            start = extracted_link.rfind('/') + 1 #get the last "/" and ahead of it, is the file name
            name = extracted_link[start:]
            extension = name.split('.')[-1]

            file_name = secure_filename(f"{name}")

            file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

            if os.path.exists(file_path):
                return {'link': f"http://192.168.29.53:5000/download/{file_name}"}

            try:
                response = session.get(extracted_link)
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                return {'link': f"http://192.168.29.53:5000/download/{file_name}"}

            except:
                return "Error downloading file"




def get_attendance_summary(cookies) -> list[dict]:
    """
        Fetches the link, parses and organises the data into a neat JSON array.

        Parameters:
            link: link to be fetched
            cookies: session data to persist

        Returns:
            An Array of JSON Objects with the following attributes  

            - subject : subject name
            - total : total no. of classes
            - present : no. of classes attended
            - absent : no. of classes missed
            - percentage: ratio of present/absent 
    """


    with requests.session() as session:

        #Insert the session cookies
        session.cookies = requests.utils.cookiejar_from_dict(cookie_dict=cookies)
        response = session.get(SITE.ATTENDANCE_URL)
        response = response.content

        attendance_data = PARSE.parse_attendance(response) 

        if len(attendance_data) == 0:
            return None       
        return attendance_data