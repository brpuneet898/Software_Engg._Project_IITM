from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    flash,
    abort,
    jsonify,
    session,
    Flask,
)
from flask_restful import Resource, Api
from backend.GA.llm_setup import *
from backend.GA.lecture_database import *
from backend.GA.ga_feedback import all_asg 

assgn = Blueprint(
    "assignments", __name__, static_folder="../static", template_folder="../templates"
)


@assgn.route("/analyze", methods=["POST"])
def submission_analysis():
    if request.method == "POST":
        selected_options = request.form
        
        # Check if any options were selected
        if not any(selected_options.getlist(key) for key in selected_options if "question-" in key):
            return jsonify({"error": "No options selected!"})

        # Print the submitted form data to the console
        week_id = selected_options.get("week")
        results = {}
        counter = 0
        grp_counter = 0
        weeks_questions = all_asg[int(week_id)]

        for i, bulk_question in weeks_questions.items():
            grp_counter += 1
            results[grp_counter] = {}

            bulk_context = bulk_question[0]
            for j, question_deets in bulk_question[1].items():
                counter += 1
                act_qn = question_deets[0]
                act_opt = question_deets[1]
                act_ans = sorted(question_deets[2])
                this_name = "question-" + str(counter)

                selected_answers = sorted(selected_options.getlist(this_name))

                if selected_answers == act_ans:
                    results[grp_counter][j] = {
                        "status": "Correct",
                        "selected": selected_answers
                    }
                elif set(selected_answers).intersection(set(act_ans)):
                    # Determine if the selected answers are partially correct
                    correct_selected = set(selected_answers).intersection(set(act_ans))
                    if correct_selected and len(selected_answers) != len(act_ans):
                        results[grp_counter][j] = {
                            "status": "Partially Correct",
                            "selected": selected_answers
                        }
                    else:
                        results[grp_counter][j] = {
                            "status": "Incorrect",
                            "selected": selected_answers
                        }
                else:
                    results[grp_counter][j] = {
                        "status": "Incorrect",
                        "selected": selected_answers
                    }

        feedback, raw_feedback = feedback_gen(week_id, results)
        return jsonify({"results": results, "feedback": feedback, "raw_feedback": raw_feedback})

@assgn.route("/analyze_doubt", methods=["POST"])
def analyze_doubt():
    if request.method == "POST":
        question_index = request.form.get("question_index")
        doubt = request.form.get("doubt")
        week_id = request.form.get("week")
        print(question_index)
        print(doubt)
        print(week_id)

        results = {}
        counter = 0
        grp_counter = 0
        weeks_questions = all_asg[int(week_id)]
        print("new")
        # print(weeks_questions)
        for i, bulk_question in weeks_questions.items():
            # print(bulk_question)
            # print("yo")
            grp_counter += 1
            results[grp_counter] = {}

            bulk_context = bulk_question[0]
            for j, question_deets in bulk_question[1].items():
                counter += 1
                if counter == int(question_index):
                    act_qn = question_deets[0]
                    act_opt = question_deets[1]
                    act_ans = question_deets[2]
                    act_ans.sort()

                    print("_________strt____________")
                    print(act_qn)
                    print(act_opt)
                    print(act_ans)

                    print("_________nxt____________")

                    # send the doubt top the llm
                    cleared_doubt = individual_doubt(
                        doubt=doubt,
                        question=act_qn,
                        options=act_opt,
                        answer=act_ans,
                        context=bulk_context,
                    )

                    return jsonify(cleared_doubt)
            else:
                print("searcgubf")
                continue

    return jsonify("No question found")


@assgn.route("/dashboard/gradedassignment/<week_id>")
def gradedassignment(week_id):
    """
    ---
    get:
      summary: Graded Assignment Page
      description: Graded Assignment Page populated with details
      responses:
        200:
          description: Success
    """

    # print("week_id",week_id)

    weeks_asg = all_asg[int(week_id)]
    week_lecture_counts = {
        1: 7,  # Week 1: 7 lectures
        2: 5,  # Week 2: 5 lectures
        3: 6,  # Week 3: 6 lectures
        4: 6   # Week 4: 6 lectures
    }
    # print(weeks_asg)
    return render_template("ga_copy.html", weeks_asg=weeks_asg, week_id=week_id, results={},user_info = session['user'],lecture_links = week_lecture_counts)
from flask import render_template, request, redirect, url_for, session

@assgn.route("/submit", methods=["POST"])
def temp_submission():
    if request.method == "POST":
        selected_options = request.form
        week_id = selected_options.get("week")

        results = {}
        total_marks = 0
        obtained_marks = 0
        counter = 0
        grp_counter = 0
        weeks_questions = all_asg.get(int(week_id), {})

        for i, bulk_question in weeks_questions.items():
            grp_counter += 1
            results[grp_counter] = {}

            for j, question_deets in bulk_question[1].items():
                counter += 1
                total_marks += 1  # Each question is 1 mark
                act_ans = sorted(question_deets[2])
                selected_answers = sorted(selected_options.getlist(f"question-{counter}"))

                if selected_answers == act_ans:
                    results[grp_counter][j] = {
                        "status": "Correct",
                        "selected": selected_answers
                    }
                    obtained_marks += 1
                elif set(selected_answers).intersection(set(act_ans)):
                    # Determine if the selected answers are partially correct
                    correct_selected = set(selected_answers).intersection(set(act_ans))
                    if correct_selected and len(selected_answers) != len(act_ans):
                        # Calculate partial marks
                        partial_marks = len(correct_selected) / len(act_ans)
                        results[grp_counter][j] = {
                            "status": "Partially Correct",
                            "selected": selected_answers
                        }
                        obtained_marks += partial_marks
                    else:
                        results[grp_counter][j] = {
                            "status": "Incorrect",
                            "selected": selected_answers
                        }
                else:
                    results[grp_counter][j] = {
                        "status": "Incorrect",
                        "selected": selected_answers
                    }

        # Calculate percentage
        if total_marks > 0:
            percentage = int((obtained_marks / total_marks) * 100)
        else:
            percentage = 0

        week_lecture_counts = {
            1: 7,  # Week 1: 7 lectures
            2: 5,  # Week 2: 5 lectures
            3: 6,  # Week 3: 6 lectures
            4: 6   # Week 4: 6 lectures
        }

        from models import Student, Grades, db
        #save the obtained marks in the database
        if 'user' in session:
            user_info = session['user']
            if 'email' in user_info:
                email = user_info['email']
                user = Student.query.filter_by(email=email).first()
                if user is None:
                    user = Student(email=email)
                    db.session.add(user)
                    db.session.commit()

                #save the obtained marks in the database
                if Grades.query.filter_by(student_id=user.id, week_id=week_id).first():
                    Grades.query.filter_by(student_id=user.id, week_id=week_id).update({"grade": percentage})
                    db.session.commit()
                else: 
                    grade = Grades(student_id=user.id, week_id=week_id, grade=percentage)
                    db.session.add(grade)
                    db.session.commit()

        return render_template(
            "ga_copy.html",
            weeks_asg=weeks_questions,
            week_id=week_id,
            results=results,
            selected_options=selected_options,
            user_info=session.get('user'),
            lecture_links=week_lecture_counts,
        )


# TODO
@assgn.route("/api/complete_assignment_feedback", methods=["POST"])
def process_questionnaire():
    """
    ---
    post:

      summary: Generate student custom feedback
      description: Endppoint to generate student custom feedback based on the questionnaire and student responses.
      responses:
        200:
          description: Success
    """
    # input format: [[question, options, marked_answer, correct_answer]]
    # [
    # ["What is Flask?", ["A web framework", "A type of container"], "A web framework", "A web framework"],
    # ["What is Python?", ["A programming language", "A snake"], "A programming language", "A snake"]
    # ]

    data = request.get_json()

    question_options_markedanswer_correctanswer = []

    # Process each question
    for item in data:
        question = item[0]
        options = item[1]
        marked_option = item[2]
        correct_option = item[3]

        # Create a formatted string for each question
        question_str = f"Question: {question}, Options: {', '.join(options)}, Marked Option: {marked_option}, Correct Option: {correct_option}"
        question_options_markedanswer_correctanswer.append(question_str)

    # Combine all questions into a single line response
    single_line_response = " | ".join(question_options_markedanswer_correctanswer)

    # Return the response as JSON
    return jsonify({"response": single_line_response})


@assgn.route("/api/process_regular_questions", methods=["POST"])
def process_questions():
    """
    ---
    post:

      summary: Chatbot for regular questions
      description: Endpoint to process regular questions and generate responses from LLM.
      responses:
        200:
          description: Success
    """
    data = request.get_json()
    question = data.get("question", "")
    options = data.get("options", [])

    # replace this with the function Aryan, for example question_answer = functioncall()
    question_answer = f"Main question: {question}\n Options: {', '.join(options)}"

    # Return the response as JSON
    return jsonify({"response": question_answer})



@assgn.route("/api/gradedassignment/<week_id>/clear")
def gradedassignmentreset(week_id):
    """
    ---
    delete:

      summary: Clear Graded Assignment
      description: Clear the answers of the current graded assignment

      responses:
        200:
          description: Success
    """

    weeks_asg = all_asg[int(week_id)]
    # print(weeks_asg)
    return redirect(url_for("assignments.gradedassignment", week_id=week_id))


@assgn.route("/api/dashboard/gradedassignment/<week_id>")
def gradedassignment_api(week_id):
    """
    ---
    post:
      summary: Graded Assignment Page Details
      description: Graded Assignment Page populated with details

      responses:
        200:
          description: Success
    """

    weeks_asg = all_asg[int(week_id)]
    # print(weeks_asg)
    return jsonify({"weeks_asg": weeks_asg, "week_id": week_id})


@assgn.route("/api/per_qn_explaination", methods=["POST"])
def per_qn_explaination():
    """
    ---
    post:

      summary: Generates explanation for individual question
      description: Endpoint to generate explanation for individual question without user query.
      responses:
        200:
          description: Success
    """
    if request.method == "POST":
        question = request.form.get("question")
        doubt = "Please explain this question more elaborately to me."
        response = individual_doubt(question, doubt)
        return jsonify({"response": response})


@assgn.route("/api/per_qn_doubt", methods=["POST"])
def per_qn_doubt():
    """
    ---
    post:
      summary: Generates explanation for individual question based on doubt
      description: Endpoint to generate explanation for individual question with user query.
      responses:
        200:
          description: Success
    """
    if request.method == "POST":
        question = request.form.get("question")
        doubt = request.form.get("doubt")
        response = individual_doubt(question, doubt)
        return jsonify({"response": response})


@assgn.route("/api/verify_assignments", methods=["POST"])
def verify_assignments():
    """
    ---
    post:

      summary: Verifies assignment
      description: Endpoint to verify the responses that the user has given.
      responses:
        200:
          description: Success
    """
    if request.method == "POST":
        selected_options = request.form
        print("submit just took place")

        # Print the submitted form data to the console
        week_id = selected_options.get("week")
        print(week_id)
        print(selected_options)
        print("hiiiiiiiiiiiiiiiii")
        # print(all_asg)

        results = {}
        counter = 0
        grp_counter = 0
        weeks_questions = all_asg[int(week_id)]
        print("new")
        # print(weeks_questions)
        for i, bulk_question in weeks_questions.items():
            # print(bulk_question)
            # print("yo")
            grp_counter += 1
            results[grp_counter] = {}

            bulk_context = bulk_question[0]
            for j, question_deets in bulk_question[1].items():
                counter += 1
                print(question_deets)

                act_qn = question_deets[0]
                act_opt = question_deets[1]
                act_ans = question_deets[2]
                act_ans.sort()
                this_name = "question-" + str(counter)

                selected_answers = selected_options.getlist(this_name)
                selected_answers.sort()

                # print("_________strt____________")
                # print(act_qn)
                # print(act_opt)
                # print(act_ans)
                # print(selected_answers)
                # print("_________nxt____________")

                print(grp_counter)
                print(j)
                if selected_answers == act_ans:
                    results[grp_counter][j] = "Correct"

                else:
                    results[grp_counter][j] = "Incorrect"

        print("___________hia____________")
        print(results)

        return jsonify(results)
