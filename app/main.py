from flask import Flask, request, render_template, make_response, jsonify, url_for
from flask_cors import CORS
import os
import redis
from hashlib import sha256
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, set_refresh_cookies,
    get_jwt_identity, set_access_cookies,
)

application = Flask(__name__)
CORS(application)


application.config['JWT_TOKEN_LOCATION'] = ['cookies']
application.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300
application.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
application.config['JWT_COOKIE_CSRF_PROTECT'] = False
application.config['JWT_SECRET_KEY'] = 'super-secret'

jwt = JWTManager(application)

db = redis.from_url(os.environ.get("REDIS_URL"))


@application.route('/', methods=['GET'])
def app_index():
    return render_template('welcome.html', error=db)


@application.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
def login():
    username = request.form.get('login', None)
    password = request.form.get('password', None)
    password_hash = sha256(password.encode()).hexdigest().encode()
    if password_hash != db.hget('users', username):
        return render_template('login.html', error="Invalid login or password.")

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    resp = redirect_resp('/')
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


def redirect_resp(url):
    resp = make_response('', 303)
    resp.headers['Location'] = url
    return resp


@application.route('/api/example', methods=['GET'])
@jwt_required
def protected():
    username = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(username)}), 200


@application.route('/register/', methods=['GET'])
def register_view():
    return render_template('register.html')


@application.route('/user/<username>', methods=['GET'])
def user_exists(username):
    response = jsonify({'exists': False})
    if db.hexists('users', username):
        response = jsonify({'exists': True})
    return response


@application.route('/create-user', methods=['POST'])
def save_user():
    form = request.form
    user = {
        'login': form['login'],
        'email': form['email'],
        'password': form['password']
    }

    password_hash = sha256(user['password'].encode()).hexdigest()
    db.hset('users', user['login'], password_hash)

    return render_template('welcome.html')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 80)))
