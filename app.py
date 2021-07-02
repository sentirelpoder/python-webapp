import logging
import json
import copy

from flask import Flask, render_template, redirect, url_for, request, session, json
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

#@author Setenay Ronael İkiz

app = Flask(__name__)
app.secret_key = "Udacity-Secret-Key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

session_user = None

class User(UserMixin):
    def __init__(self, name, age):
        self.id = name
        self.name = name
        self.age = age

    def get_id(self):
        return self.name

    @property
    def is_authenticated(self):
        return self.age >= 18


def get_user():
    return copy.copy(session_user)


@login_manager.user_loader
def user_loader(id):
    return get_user()


@login_manager.request_loader
def request_loader(request):
    return session_user


@app.route('/status')
def healthcheck():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response


@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, "data": {"UserCount": 140, "UserCountActive": 23}}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    global session_user
    if session_user is not None:
        return redirect(url_for('welcome'))
    if request.method == 'GET':
        return render_template('login.html')

    user = User(request.form.get('name'), int(request.form['age']))
    if user.is_authenticated:
        login_user(user)
        session_user = copy.copy(current_user)
        return redirect(url_for('welcome'))

    return app.response_class(
        response=json.dumps({"message": "Sorry " + user.name + ". You are not authorized."}),
        status=401,
        mimetype='application/json'
    )


@app.route('/logout', methods=['POST'])
def logout():
    global session_user
    session_user = None
    logout_user()
    session.clear()
    return redirect(url_for('login'))



@app.route('/welcome')
@login_required
def welcome():
    return render_template("welcome.html", name=current_user.id)


@app.route("/")
def hello():
    app.logger.info('Main request successfull')
    if '_user_id' in session:
        return redirect('welcome')
    return redirect(url_for('login'))


if __name__ == "__main__":
    ## stream logs to a file
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(host='0.0.0.0', port=8080)
