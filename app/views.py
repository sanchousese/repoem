import os
from datetime import datetime
from app import app, db, auth
from flask import Flask, abort, request, jsonify, g, url_for, json, render_template, redirect
from flask.ext.cors import CORS, cross_origin
from werkzeug import secure_filename
from app.models import User, PoemFile
from sqlalchemy.sql import func
import string 
import random
import subprocess

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
ALLOWED_EXTENSIONS = set(['txt'])

@app.route('/')
@app.route('/index')
@cross_origin()
def index():
  return "Hello, world!"


@app.route('/api/new_user', methods = ['POST'])
@cross_origin()
def new_user():
  login = request.json.get('login')
  email = request.json.get('email')
  password = request.json.get('password')

# TODO: add normal error handling
  if (email is None) or (password is None):
    abort(400)
  if User.query.filter_by(email = email).first() is not None:
    abort(400)
  user = User(email = email, login = login)
  user.hash_password(password)
  db.session.add(user)
  db.session.commit()
  return json.dumps(user.serialize()), 201, {'Location': url_for('get_user', id = user.id, _external=True)}

@app.route('/api/users/<int:id>')
@cross_origin()
def get_user(id):
  user = User.query.get(id)
  if not user:
    abort(400)
  return json.dumps(user.serialize())


@app.route('/api/token')
@cross_origin()
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token(600)
  return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@cross_origin()
@auth.login_required
def get_resource():
  return jsonify({'data': 'Hello, %s!' % g.user.login})

@app.route('/upload_poem')
@cross_origin()
def upload_poem():
  return render_template('poem_files.html')

@app.route('/api/poem/<token>')
@cross_origin()
def get_poem_file(token):
  poem_file = PoemFile.query.filter_by(token = token).first()
  if not poem_file:
    abort(400)
  return json.dumps(poem_file.serialize())

@app.route('/api/poem_files', methods = ['POST'])
@cross_origin()
def poem_files():
  file = request.files['file']
  if file and allowed_file(file.filename):
    file_token = token_generator()
    while PoemFile.query.filter_by(token = file_token).first() is not None:
      file_token = token_generator()

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_token))
    poem_file = PoemFile(token = file_token, trained = False)
    db.session.add(poem_file)
    db.session.commit()

    subprocess.Popen(['python', 'network.py', os.path.dirname(os.path.realpath(__file__)) + '/../assets/' + file_token])

    print json.dumps(poem_file.serialize()), 201, {'PoemFile': url_for('get_poem_file', token = file_token, _external=True)}

    return render_template('success.html')

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
  
def token_generator(size=32, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))