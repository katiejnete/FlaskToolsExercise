import os
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey
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
    """Shows start page of survey."""
    return render_template(
        'base.html',title=survey.title, instrucs=survey.instructions)

@app.route("/session", methods=["POST"])
def start_session():
    """Clear session of responses and asked questions."""
    if request.method == 'POST':
        session['responses'] = []
        responses = session['responses']
        num = len(responses)
        return redirect(f"/questions/{str(num)}")

@app.route("/questions/<int:num>")
def question_handler(num):
    """Displays current question."""
    responses = session['responses']
    if len(responses) == len(survey.questions):
        return redirect("/thanks")
    elif int(num) == len(responses):
        q = survey.questions[int(num)]
        return render_template(
            'q.html',qnum=num,title=survey.title, instrucs=survey.instructions,q=q.question,choices=q.choices)
    else:
        flash('You are tying to access an invalid question. Please answer questions in order.','invalid')
        new_num = len(responses)
        return redirect(f"/questions/{new_num}")      

@app.route("/answer", methods=["POST"])
def answer_handler():
    """Saves responses and redirects to next question."""
    responses = session['responses']
    if request.method == "POST":
        if  len(responses) == len(survey.questions):
            ans = request.form['answer']
            responses.append(ans)
            session['responses'] = responses
            return redirect("/thanks")
        else:
            ans = request.form['answer']
            responses.append(ans)
            session['responses'] = responses
            num = len(responses)            
            return redirect(f"/questions/{num}")

@app.route("/thanks")
def thank_user():
    """Survey complete. Shows 'Thank You' page."""
    session.pop('responses', default=None)
    return render_template(
        'thanks.html',title=survey.title, instrucs=survey.instructions)