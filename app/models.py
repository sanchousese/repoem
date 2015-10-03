from flask import g, json, jsonify
from app import app, db, auth
from sqlalchemy.inspection import inspect
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
						  as Serializer, BadSignature, SignatureExpired)


class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	login = db.Column(db.String(16), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	password_hash = db.Column(db.String(127))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def generate_auth_token(self, expiration = 600):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None    # valid token, but expired
		except BadSignature:
			return None    # invalid token
		user = User.query.get(data['id'])
		return user

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def serialize(self):
		d = self.as_dict()
		del d['password_hash']
		return d

	def __repr__(self):
		return '<User %r>' % (self.login)


@auth.verify_password
def verify_password(email_or_token, password):
	# first try to authenticate by token
	user = User.verify_auth_token(email_or_token)
	if not user:
		# try to authenticate with username/password
		user = User.query.filter_by(email = email_or_token).first()
		if not user or not user.verify_password(password):
			return False
	g.user = user
	return True
