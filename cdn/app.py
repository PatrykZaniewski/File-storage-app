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
  if len(uid) == 0:
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
  if f.filename is "":
    return redirect(f"{c}?error=No+file+provided") if c \
    else ('<h1>CDN</h1> No file provided', 400)
  if t is None:
    return redirect(f"{c}?error=No+token+provided") if c \
    else ('<h1>CDN</h1> No token provided', 401)
  if not valid(t):
    return redirect(f"{c}?error=Invalid+token") if c \
    else ('<h1>CDN</h1> Invalid token', 401)
  payload = jwt.decode(t, JWT_SECRET)
  if payload.get('uid') != uid or payload.get('action') != 'upload':
    return '<h1>CDN</h1> Incorrect token payload', 401

  if not os.path.exists("/tmp/" + uid):
    os.mkdir("/tmp/" + uid)

  #TODO zrobic zamykanie zeby czekalo na save'a
  content_type = "multipart/form-data"
  f.save('/tmp/' + uid + "/" + f.filename)
  f.close()

  return redirect(f"{c}?uid={uid}&content_type={content_type}") if c \
  else (f'<h1>CDN</h1> Uploaded {uid}', 200)

def valid(token):
  try:
    jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
  except jwt.InvalidTokenError as e:
    app.logger.error(str(e))
    return False
  return True

def redirect(location):
  response = make_response('', 303)
  response.headers["Location"] = location
  return response