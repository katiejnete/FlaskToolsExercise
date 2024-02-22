import os
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', default='BAD_SECRET_KEY')

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_USE_SIGNER'] = True

debug = DebugToolbarExtension(app)
Session(app)

@app.route("/")
def start_survey():
    """Shows start page with survey title, instructions, and button to start survey."""
    return render_template('base.html',title=satisfaction_survey.title, instrucs=satisfaction_survey.instructions)

@app.route("/session", methods=["POST"])
def start_session():
    if request.method == 'POST':
        session['responses'] = []
        session['asked'] = []
        responses = session['responses']
        num = len(responses)
        return redirect(f"/questions/{str(num)}")

@app.route("/questions/<num>")
def question_handler(num):
    """Handles URLs like /questions/0 and so on. Shows form asking current question
    with radio buttons as choices. Once answered and submitted,
    then POST request and next question happens."""
    responses = session['responses']
    asked = session['asked']
    if len(responses) == len(satisfaction_survey.questions):
        return redirect("/thanks")
    elif int(num) == len(responses):
        q = satisfaction_survey.questions[int(num)]
        form_name = 'q' + num
        asked.append(form_name)
        session['asked'] = asked
        return render_template('q.html',title=satisfaction_survey.title, instrucs=satisfaction_survey.instructions,q=q.question,choices=q.choices,name=form_name)
    else:
        flash('You are tying to access an invalid question. Please answer questions in order.','invalid')
        new_num = len(responses)
        return redirect(f"/questions/{str(new_num)}")      

@app.route("/answer", methods=["POST"])
def answer_handler():
    """When user submits answer, append my answer to my responses list.
    Redirects to next question."""
    responses = session['responses']
    asked = session['asked']
    if request.method == "POST":
        if  len(responses) == len(satisfaction_survey.questions):
            just_asked = asked[len(asked)-1]
            ans = request.form[just_asked]
            responses.append(ans)
            session['responses'] = responses
            return redirect("/thanks")
        else:
            just_asked = asked[len(asked)-1]
            ans = request.form[just_asked]
            next_q_num = str(len(asked))
            responses.append(ans)
            session['responses'] = responses            
            return redirect(f"/questions/{next_q_num}")

@app.route("/thanks")
def thank_user():
    """Thank user after user finished all questions."""
    session.pop('responses', default=None)
    session.pop('asked', default=None)
    return render_template('thanks.html',title=satisfaction_survey.title, instrucs=satisfaction_survey.instructions)