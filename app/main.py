from flask import Flask, request, render_template, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = {}

@app.route('/', methods=['GET'])
def app_index():
    return render_template('register.html')

@app.route('/user/<username>', methods=['GET'])
def user_exists(username):
    response = make_response('', 404)
    if username in users:
        response.status_code = 200
    return response

@app.route('/register', methods=['POST'])
def save_user():
    form = request.form
    user = {
        'login': form['login'],
        'email': form['email'],
        'password': form['password']
    }
    users[form['login']] = user

    return make_response('', 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
