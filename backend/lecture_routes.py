from flask import render_template,request,redirect,url_for,Blueprint,flash,abort,jsonify, Flask,session
from flask_restful import Resource, Api
from backend.GA.llm_setup import *
from backend.GA.lecture_database import *
from backend.GA.lecture_database import *


lec = Blueprint("lecture_routes",__name__,static_folder = '../static',template_folder="../templates" )

@lec.route('/dashboard/lecture/<week_id>/<lecture_id>', methods=['GET'])
def lecture(week_id,lecture_id):

    """
    ---
    get:
      summary: Lecture Page
      description: Route for lecture page
      responses:
        200:
          description: Success
    """       
    lecture_link = lectures_db[int(week_id)][int(lecture_id)]

    def convert_to_embed_url(youtube_url):
        # print(youtube_url)
        video_id = youtube_url[0].split(".be/")[-1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return embed_url  
    
    embed_url = convert_to_embed_url(lecture_link)
    lec_transcript = lecture_link[1]
    lec_summary = get_summary(lec_transcript)
    lec_key = get_key(lec_transcript)
    week_lecture_counts = {
        1: 7,  # Week 1: 7 lectures
        2: 5,  # Week 2: 5 lectures
        3: 6,  # Week 3: 6 lectures
        4: 6   # Week 4: 6 lectures
    }
    return render_template('lecture_copy.html', lecture_link=embed_url,lecture_id=lecture_id,week_id=week_id,lec_summary=lec_summary,lec_key=lec_key,user_info=session['user'],lecture_links = week_lecture_counts),200

# TODO
@lec.route('/api/lecture_populate', methods=['POST'])
def lecture_populate():

    """
    ---
    post:
      summary: Populates lecture pages
      description: Endpoint to populate lectures pages.
      responses:
        200:
          description: Success
    """    
    return jsonify({"message":"success"}),200