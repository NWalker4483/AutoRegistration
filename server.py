from classes import Manager, Student
import utils.websis as websis
from flask import Flask, request, render_template
import threading
import auth
import logging
import sys
import time
logging.basicConfig(filename='AutoRegistration.log', format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)

app = Flask("AutoRegistration")
app.logger.addHandler(handler)


@app.route('/')
def my_form():
    global manager
    return render_template('form.html', courses=available_courses)


@app.route('/check', methods=['POST'])
def CheckCourseSubscriptions():
    global manager


@app.route('/subscribe', methods=['POST'])
def ProcessCourseSubscribtionForm():
    global manager
    MSU_USERNAME = request.form['username'].strip()
    MSU_PASSWORD = request.form.get('password', None)
    ALT_PIN = request.form.get('alt_pin', None) # TODO: Add Constraints to html form 
    
    TERM_IN = websis.CURRENT_TERM_ID
    SUBJECT, COURSE_ID = request.form["course"].split()
    CRN = request.form['crn'] # TODO: Add Constraints to html form 
    new_student = Student(MSU_USERNAME, MSU_PASSWORD)
    
    msg = f"Added {MSU_USERNAME} to {SUBJECT} {COURSE_ID} : {CRN} list behind {'null'} others"
    
    if not manager.hasInfoFor(MSU_USERNAME):
        if ALT_PIN != None: # If the user is attempting to use the registration service
        # Validate Login Info
            if websis.WebsisSessionIsActive(websis.LoginToWebsis(new_student)):
                manager.AddStudent(new_student)
            else:
                msg = "Websis Login Failed Check Info "
                app.logger.error(f"Websis Login Failed Check Info for {MSU_USERNAME}")
        else:
            manager.AddStudent(new_student)

    if manager.hasInfoFor(MSU_USERNAME):
        manager.AddCourseSubscribtion(
            TERM_IN, SUBJECT, COURSE_ID, CRN, MSU_USERNAME)
        app.logger.info(msg)

    return render_template('form.html', message=msg, courses=available_courses)


def ScheduleWebsisCheck(t=60):
    global manager
    manager.CheckCourseAvailability()
    threading.Timer(t, ScheduleWebsisCheck).start()


if __name__ == "__main__":
    manager = Manager()
    available_courses = websis.get_available_courses(
        manager.getMasterSess(), websis.CURRENT_TERM_ID)
    ScheduleWebsisCheck(600)  # Seconds
    app.run(debug=True)
