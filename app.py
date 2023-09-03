from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
# from surveys import satisfaction_survey as survey
from surveys import Survey, Question, surveys

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these
RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def choose_survey():
    """Choose a survey"""

    return render_template("choose_survey.html", survey_options=surveys)


@app.route("/chosen_survey", methods=["POST"])
def chosen_survey():
    """Initiate chosen survey"""

    chosen_survey = request.form["survey_choice"]
    session["chosen_survey"] = chosen_survey

    return redirect("/survey_start")


@app.route("/survey_start")
def show_survey_start():
    """Start the selected survey."""

    chosen_survey = session["chosen_survey"]
    survey = surveys[chosen_survey]

    return render_template("survey_start.html", survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    choice = request.form['answer']

    # add this response to the session
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    chosen_survey = session["chosen_survey"]
    survey = surveys[chosen_survey]

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    responses = session.get(RESPONSES_KEY)
    chosen_survey = session["chosen_survey"]
    survey = surveys[chosen_survey]

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    if (len(responses) != qid):
        # Trying to access questions out of order.
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    
    chosen_survey = session["chosen_survey"]
    survey = surveys[chosen_survey]
    return render_template("completion.html", survey=survey)
