from uuid import uuid4
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from flask import session as se
from dotenv import load_dotenv
from os import getenv
import datetime
import redisHandler
import sessionHandler
import redis
import jwt
import requests
import json

load_dotenv(verbose=True)

HTML = """<!doctype html>
<head><meta charset="utf-8"/></head>"""

app = Flask(__name__)
app.secret_key = "super secret key"
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

fileStatus = ''

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return redirect("/login")
    return redirect("/index")


@app.route('/login', methods=['GET'])
def login():
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            return redirect("/index")
    return render_template("login.html")


@app.route('/index')
def welcome():
    err = se.get('err')
    se['err'] = ''
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            message = createFileMessage(err)
            uid = session.getNicknameSession(session_id)
            downloadToken = createDownloadToken(uid).decode('utf-8')
            uploadToken = createUploadToken(uid).decode('utf-8')
            listToken = createListToken(uid).decode('utf-8')
            deleteToken = createDeleteToken(uid).decode('utf-8')
            listOfFiles = json.loads(requests.get("http://cdn:5000/list/" + uid + "?token=" + listToken).content)
            return render_template("index.html", uid=uid, uploadToken=uploadToken, downloadToken=downloadToken,
                                   listOfFiles=listOfFiles, deleteToken=deleteToken, message=message)
        else:
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
    err = request.args.get('error')
    print(err, flush=True)
    if session_id:
        if session.checkSession(session_id):
            se['err'] = err
    return redirect('/login')


def createDownloadToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=333)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "download"}, JWT_SECRET, "HS256")


def createUploadToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=333)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "upload"}, JWT_SECRET, "HS256")


def createListToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=333)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "list"}, JWT_SECRET, "HS256")


def createDeleteToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=333)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "delete"}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response

def createFileMessage(err):
    message = ''
    print(err, flush=True)
    if err == "no file provided":
        message = f'<div class="error">Nie wybrano pliku!</div>'
    elif err == "missing file":
        message = f'<div class="error">Wybrany plik nie istnieje!</div>'
    elif err == "missing uid":
        message = f'<div class="error">Nieprawidłowy użytkownik!</div>'
    elif err == "no token provided":
        message = f'<div class="error">Brak tokenu - odśwież stronę!</div>'
    elif err == "invalid token":
        message = f'<div class="error">Token nieprawidłowy lub ważność wygasła!</div>'
    elif err == "invalid token payload":
        message = f'<div class="error">Niezgodność tokenu z użytkonikiem i/lub akcją!</div>'
    elif err == "deleted":
        message = f'<div class="info">Plik usunięto!</div>'
    elif err == "ok":
        message = f'<div class="info">Plik dodano!</div>'
    return message
