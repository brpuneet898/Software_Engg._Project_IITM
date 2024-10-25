from flask_restful import Resource, Api
from backend.GA.llm_setup import *
from backend.GA.lecture_database import *
from flask import Flask, render_template, request, jsonify, Blueprint, url_for,json,redirect,session
from models import Student,Grades

# Initialize
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Register Blueprints
with app.app_context():
    from backend.lecture_routes import lec
    from backend.assignments import assgn
    from backend.chat_routes import chatt
    from models import db
    db.init_app(app)
    app.register_blueprint(lec)
    app.register_blueprint(assgn)
    app.register_blueprint(chatt)
    db.create_all()

# OAuth 2.0 Configuration
from oauthlib.oauth2 import WebApplicationClient
import requests
import os

app.secret_key = os.urandom(24)  # Needed to use session

# OAuth 2.0 Configuration
CLIENT_ID = "1098906111028-gakcsjvvittc5uorvg7e9qm6nevb9a5j.apps.googleusercontent.com"  # Replace with your Google Client ID
CLIENT_SECRET = "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"  # Replace with your Google Client Secret
#REDIRECT_URI = "https://localhost:5000/google-signin"
REDIRECT_URI = "http://127.0.0.1:5000/google-signin"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Disable in production
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

client = WebApplicationClient(CLIENT_ID)

# Google OAuth 2.0 URLs
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/google-signin")
def callback():
    # Get the authorization code from the request
    code = request.args.get("code")

    # Get Google's token endpoint
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens, let's find and hit the URL
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Extract user info
    user_info = userinfo_response.json()

    # Store user info in session
    session['user'] = user_info

    return redirect(url_for("dashboard"))


@app.route("/privacy_policy")
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route("/terms_of_service")
def terms_of_service():
    return render_template('terms_of_service.html')


#Logout
@app.route('/api/logout' , methods=['DELETE'])
def logout_user():

    """
    ---
    delete:
      summary: Clear All User Data
      description: Clears all of the current users history and data
      responses:
        200:
          description: Success
    """       
    return render_template('starter-page.html'),200


@app.route('/', methods=['GET'])
def index():

    """
    ---
    get:
      summary: Home Page
      description: Route for home page
      responses:
        200:
          description: Success
    """       
    return render_template('starter-page.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():

    """
    ---
    get:
      summary: Dashboard
      description: Route for dashboard
      responses:
        200:
          description: Success
    """
    if 'user' in session:
        user_info = session['user']
        if 'email' in user_info:
            email = user_info['email']
            user = Student.query.filter_by(email=email).first()
            if user is None:
                user = Student(email=email)
                db.session.add(user)
                db.session.commit()
    
    week_lecture_counts = {
        1: 7,  # Week 1: 7 lectures
        2: 5,  # Week 2: 5 lectures
        3: 6,  # Week 3: 6 lectures
        4: 6   # Week 4: 6 lectures
    }
    
    return render_template('dashboard_copy.html',user_info=user_info, lecture_links=week_lecture_counts),200

@app.route('/dashboard/grades', methods=['GET'])
def grades():

    """
    ---
    get:
      summary: Grades
      description: Route for grades
      responses:
        200:
          description: Success
    """       
    week_lecture_counts = {
        1: 7,  # Week 1: 7 lectures
        2: 5,  # Week 2: 5 lectures
        3: 6,  # Week 3: 6 lectures
        4: 6   # Week 4: 6 lectures
    }
    #retrieve grades from database
    usermail = session['user'].get('email')
    user = Student.query.filter_by(email=usermail).first()
    if user is None:
        return render_template('grades.html',user_info = session['user'],lecture_links = week_lecture_counts,grades = []),200
    
    grades = Grades.query.filter_by(student_id=user.id).all()
    return render_template('grades.html',user_info = session['user'],lecture_links = week_lecture_counts,grades=grades),200


@app.route('/dashboard/chatbot', methods=['GET'])
def chatbot():
       
    """
    ---
    get:
      summary: Central Chatbot 
      description: Route for chatbot interface
      responses:
        200:
          description: Success
    """           
    return render_template('chatbot.html',mail = session['user'].get('email')),200



if __name__ == '__main__':
    app.run(debug=True,port=5000)