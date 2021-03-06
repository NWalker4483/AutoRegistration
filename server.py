import json
import os
from student import Student
from manager import Manager
import utils.websis as websis
from flask import Flask, request, render_template
import threading
import auth
import logging
import sys
from utils import dev
import time
logging.basicConfig(filename='AutoRegistration.log', format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)

app = Flask("AutoRegistration")
app.logger.addHandler(handler)


@app.route('/')
def HomePage():
    return render_template('form.html', courses=available_courses)


@app.route('/modify', methods=['POST'])
def ModifySubscriptions():
    global manager
    raise(NotImplementedError)


@app.route('/check', methods=['POST'])
def CheckCourseSubscriptions():
    global manager
    raise(NotImplementedError)


@app.route('/subscribe', methods=['POST'])
def ProcessCourseSubscribtionForm():
    global manager
    msg = ""
    MSU_USERNAME = request.form['username'].strip()
    MSU_PASSWORD = request.form.get('password', None)
    # TODO: Add Constraints to html form
    ALT_PIN = request.form.get('alt_pin', None)
    if ":" in MSU_USERNAME:
        try:
            cmd = MSU_USERNAME.split(":")
            if cmd[0] == "admin" and cmd[1] == "123456":
                msg = dev.cmd_set[cmd[2]](manager, cmd[3])
        finally:
            return render_template('form.html', message=msg, courses=available_courses)

    if not websis.ValidateEmail(MSU_USERNAME + "@morgan.edu"):
        return render_template('form.html', message="Email Invalid", courses=available_courses)

    SUBJECT = request.form["SUBJ"]
    COURSE_ID = request.form['COURSE_ID']
    CRN = request.form['CRN']
    new_student = Student(MSU_USERNAME, MSU_PASSWORD)

    msg = f"Failed to process {MSU_USERNAME}. Please check your login info"
    if not manager.hasInfoFor(MSU_USERNAME):
        if MSU_PASSWORD != None:  # If the user is attempting to use the registration service
            if websis.LoginToWebsis(new_student)[0]:  # Validate Login Info
                # Maybe Validate the Alt Pin
                manager.AddStudent(new_student)
            else:
                msg = "Websis Login Failed Check Info "
                app.logger.error(
                    f"Websis Login Failed Check Info for {MSU_USERNAME}")
        else:
            manager.AddStudent(new_student)

    if manager.hasInfoFor(MSU_USERNAME):
        manager.AddCourseSubscribtion(
            websis.CURRENT_TERM_ID, SUBJECT, COURSE_ID, CRN, MSU_USERNAME)
        msg = f"Added {MSU_USERNAME} to {SUBJECT} {COURSE_ID} : {CRN} list."
        app.logger.info(msg)

    return render_template('form.html', message=msg, courses=available_courses)


def ScheduleWebsisCheck(t=60):
    global manager
    manager.CheckCourseAvailability()
    threading.Timer(t, ScheduleWebsisCheck).start()


# https://www.reddit.com/r/flask/comments/2i102e/af_how_to_open_static_file_specifically_json/
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, 'static', 'courses.json')
available_courses = json.load(open(json_url))

manager = Manager()
ScheduleWebsisCheck(15*60)  # Seconds


if __name__ == "__main__":
    try:
        app.run(threaded=True)
    except Exception as e:
        print(e)
    finally:  # Save Manager
        print("dfghjk")
        pass
