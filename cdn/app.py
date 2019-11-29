import jwt
from uuid import uuid4
from flask import Flask
from flask import request
from flask import make_response
from flask import send_file
from dotenv import load_dotenv
from os import getenv
load_dotenv(verbose=True)
import json
import re
import os

app = Flask(__name__)
JWT_SECRET = getenv('JWT_SECRET')


@app.route('/list/<uid>', methods=['GET'])
def list(uid):
  token = request.args.get('token')
  if len(uid) == 0:
    return '<h1>CDN</h1> Missing uid', 404
  if token is None:
    return '<h1>CDN</h1> No token', 401
  if not valid(token):
    return '<h1>CDN</h1> Invalid token', 401
  payload = jwt.decode(token, JWT_SECRET)
  if payload.get('uid') != uid or payload.get('action') != 'list':
    return '<h1>CDN</h1> Incorrect token payload', 401

  if not os.path.exists("/tmp/" + uid):
    return json.dumps([])

  listOfFiles = os.listdir("/tmp/" + uid)
  return json.dumps(listOfFiles)


@app.route('/files', methods=['GET'])
def downloadd():
  uid = request.args.get('uid')
  token = request.args.get('token')
  filename = request.args.get('filename')
  if uid is None or len(uid) == 0:
    return '<h1>CDN</h1> Missing uid', 404
  if token is None:
    return '<h1>CDN</h1> No token', 401
  if not valid(token):
    return '<h1>CDN</h1> Invalid token', 401
  payload = jwt.decode(token, JWT_SECRET)
  if payload.get('uid') != uid or payload.get('action') != 'download':
    return '<h1>CDN</h1> Incorrect token payload', 401
  file = '/tmp/test/' + filename
  file = open(file, 'rb')
  return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/files', methods=['POST'])
def upload():
  f = request.files.get('file')
  t = request.form.get('token')
  c = request.form.get('callback')

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

def valid(token):
  try:
    jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
  except jwt.InvalidTokenError as e:
    app.logger.error(str(e))
    return False
  return True


def redirect(error):
  response = make_response("", 303)
  response.headers["Location"] = "https://web.company.com/index"
  response.headers["Content-Type"] = "multipart/form-data"
  return response