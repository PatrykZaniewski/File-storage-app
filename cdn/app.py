import jwt
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask import send_file
from dotenv import load_dotenv
from os import getenv

load_dotenv(verbose=True)

app = Flask(__name__)
JWT_SECRET = getenv('JWT_SECRET')


@app.route('/list/<uid>', methods=['GET'])
def list(uid):
    token = request.args.get('token')

    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return redirect("invalid+token+payload")
    if not os.path.exists("/tmp/" + uid):
        return json.dumps([])
    listOfFiles = os.listdir("/tmp/" + uid)
    return json.dumps(listOfFiles)


@app.route('/files', methods=['GET'])
def download():
    uid = request.args.get('uid')
    token = request.args.get('token')
    filename = request.args.get('filename')

    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'download':
        return redirect("invalid+token+payload")
    file = '/tmp/test/' + filename
    file = open(file, 'rb')
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/files', methods=['POST'])
def upload():
    f = request.files.get('file')
    t = request.form.get('token')
    uid = request.form.get('uid')

    if f is None or f.filename is "":
        return redirect("no+file+provided")
    if t is None:
        return redirect("no+token+provided")
    if not valid(t):
        return redirect("invalid+token")
    payload = jwt.decode(t, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return redirect("invalid+token+payload")
    if not os.path.exists("/tmp/" + uid):
        os.mkdir("/tmp/" + uid)
    f.save('/tmp/' + uid + "/" + f.filename)
    f.close()
    return redirect("ok")


@app.route('/delfiles', methods=['POST'])
def delete():
    uid = request.args.get('uid')
    token = request.args.get('token')
    filename = request.args.get('filename')

    if os.path.isfile("/tmp/" + uid + "/" + filename) is False:
        return redirect("missing+file")
    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'delete':
        return redirect("invalid+token+payload")
    file = '/tmp/test/' + filename
    os.remove(file)
    return redirect("deleted")


def valid(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        app.logger.error(str(e))
        return False
    return True


def redirect(error):
    response = make_response("", 303)
    response.headers["Location"] = "https://web.company.com/callback?error=" + error
    response.headers["Content-Type"] = "multipart/form-data"
    return response
