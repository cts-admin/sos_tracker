from flask_wtf import Form
from peewee import OperationalError
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, BooleanField, DecimalField, DateField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
								Length, EqualTo, InputRequired)

from models import User, Team

ALLOWED_EXTENSIONS = set(['gpx', 'txt'])

def email_exists(form, field):
	if User.select().where(User.email == field.data).exists():
		raise ValidationError('User with that email already exists!')

def name_exists(form, field):
	if User.select().where(User.username == field.data).exists():
		raise ValidationError('User with that name already exists!')

def validate_extension(form, field):
	"""Does filename have the right extension?"""
	if not '.' in field.data.filename and field.data.filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
		raise ValidationError('Only .txt and .gpx file extensions are permitted for upload.')

class CoordFile(Form):
	file = FileField(validators=[
		InputRequired(),
		validate_extension,
	])
	publish = BooleanField('Public?')

class RegisterForm(Form):
	username = StringField(
		'Username',
		validators=[
			InputRequired(),
			Regexp(
				r'^[a-zA-Z0-9_]+$',
				message="Username should be one word; letters, numbers, and underscores only."
			),
			name_exists
		])
	email = StringField(
		'Email',
		validators=[
			InputRequired(),
			Email(),
			email_exists
		])
	password = PasswordField(
		'Password',
		validators=[
			InputRequired(),
			Length(min=10),
			EqualTo('password2', message='Passwords must match')
		])
	password2 = PasswordField(
		'Confirm Password',
		validators=[InputRequired()]
		)
	team = SelectField('Team', coerce=int)
	code = StringField('Code', validators=[InputRequired(),])

	def validate(self):
		if not Form.validate(self):
			return False
		result = True
		team_field = self.team
		code_field = self.code
		team_object = Team.select().where(Team.id == team_field.data).get()
		if team_object.code != code_field.data:
			code_field.errors.append("Given code does not match Team code.")
			result = False
		return result

class LoginForm(Form):
	email = StringField('Email', validators=[InputRequired(), Email()])
	password = PasswordField('Password', validators=[InputRequired()])

class CreateCoordForm(Form):
	name = StringField(
		'Name',
		validators=[
			InputRequired()
		])
	latitude = DecimalField(
		'Latitude',
		validators=[InputRequired()],
		)
	longitude = DecimalField(
		'Longitude',
		validators=[InputRequired()],
		)
	pin = StringField('Pin')
	notes = TextAreaField(
		'Notes',
		validators=[InputRequired()])
	last_visit = DateField('Date Last Visited')
	published = BooleanField('Public?')