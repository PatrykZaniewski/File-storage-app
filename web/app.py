from jwt import encode, InvalidTokenError
from uuid import uuid4
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from dotenv import load_dotenv
from os import getenv
import datetime
import redisHandler
import sessionHandler
import redis

load_dotenv(verbose=True)

HTML = """<!doctype html>
<head><meta charset="utf-8"/></head>"""

app = Flask(__name__)
CDN = getenv("CDN_HOST")
WEB = getenv("WEB_HOST")
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

redis = redis.Redis(host="redis", port="6379")

redisConn = redisHandler.RedisHandler(redis)
redisConn.initUser()

session = sessionHandler.SessionHandler(redis)


@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return redirect("/login")
    return redirect("/index")


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/index')
def welcome():
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            fid = session.getNicknameSession(session_id)
            token = createToken(fid).decode('ascii')
            return render_template("index.html", fid=fid, token=token)
        else:
            fid = ''
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is not "" and password is not "":
        response = make_response('', 303)

        if redisConn.checkUser(username, password) is True:
            session_id = session.createSession(username)
            response.set_cookie("session_id", session_id, max_age=SESSION_TIME)
            response.headers["Location"] = "/index"
        else:
            response.set_cookie("session_id", "INVALIDATE", max_age=1)
            response.headers["Location"] = "/login"

        return response
    return redirect("/login")


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        session.deleteSession(session_id)
        response = redirect("/login")
        response.set_cookie("session_id", "LOGGED_OUT", max_age=1)
        return response
    return redirect("/login")


@app.route('/callback')
def uploaded():
    session_id = request.cookies.get('session_id')
    fid = request.args.get('fid')
    err = request.args.get('error')
    if not session_id:
        return redirect("/login")

    if err:
        return f"<h1>APP</h1> Upload failed: {err}", 400
    if not fid:
        return f"<h1>APP</h1> Upload successfull, but no fid returned", 500
    content_type = request.args.get('content_type', 'text/plain')
    session[session_id] = (fid, content_type)
    return f"<h1>APP</h1> User {session_id} uploaded {fid} ({content_type})", 200


def createToken(fid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return encode({"iss": "web:5000", "exp": exp}, JWT_SECRET, algorithm="HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response
