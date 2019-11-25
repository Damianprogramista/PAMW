from flask import Flask, request, render_template, make_response, jsonify, send_file
from flask_cors import CORS
from functools import wraps
import os
import redis
from hashlib import sha256
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, set_refresh_cookies, unset_jwt_cookies,
    get_jwt_identity, set_access_cookies, verify_jwt_in_request, verify_jwt_in_request_optional
)
from flask_swagger_ui import get_swaggerui_blueprint

application = Flask(__name__)
CORS(application)

application.config["CACHE_TYPE"] = "null"

application.config['JWT_TOKEN_LOCATION'] = ['cookies']
application.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300
application.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
application.config['JWT_COOKIE_CSRF_PROTECT'] = False
application.config['JWT_SECRET_KEY'] = 'super-secret'

jwt = JWTManager(application)

# db = redis.from_url(os.environ.get("REDIS_URL"))
db = redis.Redis('redis')

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "PAMW"
    }
)
application.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


def not_logged_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            if get_jwt_identity():
                return redirect_resp('/')
        except Exception as e:
            pass
        return fn(*args, **kwargs)
    return wrapper


@application.route('/', methods=['GET'])
def app_index():
    user = None
    files = None
    try:
        verify_jwt_in_request_optional()
        user = get_jwt_identity()
        if user:
            user1 = "f" + str(user)
            files = db.smembers(user1)
    except Exception as e:
        print(e)

    return render_template('welcome.html', user=user, files=files)


@application.route('/login', methods=['GET'])
@not_logged_required
def login_view():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
@not_logged_required
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


def redirect_resp(url, message=None):
    resp = make_response('', 303)
    resp.headers['Location'] = url
    if message:
        resp.data['message'] = message
    return resp


@application.route("/api/upload", methods=["POST"])
@jwt_required
def upload():
    user = get_jwt_identity()
    file = request.files['pdf']
    response = redirect_resp('/')
    ext = file.filename.split(".")[-1]
    if ext != 'pdf':
        return response

    save_file(file, str(user))
    return response


def save_file(file_to_save, user):
    if len(file_to_save.filename) > 0:
        new_filename = file_to_save.filename

        path_to_file = 'files/' + new_filename
        file_to_save.save(path_to_file)
        file = {"path": path_to_file, "user": user}
        db.hmset(new_filename, file)
        user1 = "f"+user
        db.sadd(user1, new_filename)
    else:
        response = redirect_resp('/')
        return response


@application.route("/api/download/<file>", methods=['GET', 'POST'])
@jwt_required
def download_file(file):
    try:
        path = "files/"+file
        return send_file(path)
    except Exception as e:
        return make_response('Error getting file', 404)


@application.route('/register', methods=['GET'])
@not_logged_required
def register_view():
    return render_template('register.html')


@application.route('/logout')
def logout():
    response = redirect_resp('/')
    unset_jwt_cookies(response)
    return response


@application.route('/user/<username>', methods=['GET'])
def user_exists(username):
    response = jsonify({'exists': False})
    if db.hexists('users', username):
        response = jsonify({'exists': True})
    return response


@application.route('/create-user', methods=['POST'])
@not_logged_required
def save_user():
    form = request.form
    user = {
        'login': form['login'],
        'email': form['email'],
        'password': form['password']
    }

    password_hash = sha256(user['password'].encode()).hexdigest()
    db.hset('users', user['login'], password_hash)

    return make_response('', 200)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 80)))
