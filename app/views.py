from datetime import datetime
from app import app, db, auth
from flask import Flask, abort, request, jsonify, g, url_for, json
from flask.ext.cors import CORS, cross_origin
from app.models import User, Place, Image, Rating, Comment
from sqlalchemy.sql import func

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

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

