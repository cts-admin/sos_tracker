import datetime
import os
import re

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *
from playhouse.sqlite_ext import FTSModel, SqliteExtDatabase, SearchField

DATABASE = SqliteExtDatabase('sos.db')

class Team(Model):
	"""Individual SOS team."""
	name = CharField(unique=True)
	institution = CharField()
	code = CharField() # To prevent users from joining arbitrary teams

	class Meta:
		database = DATABASE
		order_by = ('name',)

	@classmethod
	def create_team(cls, name, institution, code):
		try:
			with DATABASE.transaction():
				cls.create(
					name=name,
					institution=institution,
					code=code
				)
		except IntegrityError:
			raise ValueError("Team already exists.")

class User(UserMixin, Model):
	username = CharField(unique=True)
	email = CharField(unique=True)
	password = CharField(max_length=100)
	joined_at = DateTimeField(default=datetime.datetime.now)
	is_admin = BooleanField(default=False)
	team = ForeignKeyField(
		rel_model=Team,
		related_name='users'
	)

	class Meta:
		database = DATABASE
		order_by = ('-joined_at',)

	@classmethod
	def create_user(cls, username, email, password, team, admin=False):
		try:
			with DATABASE.transaction():
				cls.create(
					username=username,
					email=email,
					password=generate_password_hash(password),
					team=team,
					is_admin=admin
				)
		except IntegrityError:
			raise ValueError("User already exists.")

	def team_users(self):
		"""The users of a team."""
		return User.select().where(User.team == self.team)

class Coordinate(Model):
	latitude = FloatField()
	longitude = FloatField()
	name = FixedCharField()
	pin = FixedCharField(null=True)
	notes = TextField()
	recommended_visit = DateField(null=True)
	slug = CharField(unique=True)
	published = BooleanField(index=True) # Coordinates/points can be made public
	timestamp = DateTimeField(default=datetime.datetime.now, index=True)
	user = ForeignKeyField(
		rel_model=User,
		related_name='coords'
	)

	class Meta:
		database = DATABASE

	def get_user_coords(self):
		return Coordinate.select().where(Coordinate.user == self)

	def get_team_coords(self):
		return Coordinate.select().where(
			(Coordinate.user << User.team_users()) |
			(Coordinate.user == self)
		)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = re.sub('[^\w]+', '-', self.name.lower())
		ret = super(Coordinate, self).save(*args, **kwargs)

		# Store search content
		self.update_search_index()
		return ret

	def update_search_index(self):
		try:
			base_coord = FTSCoord.get(FTSCoord.entry_id == self.id)
		except FTSCoord.DoesNotExist:
			base_coord = FTSCoord(entry_id=self.id)
			force_insert = True
		else:
			force_insert = False
		base_coord.content = '\n'.join((self.name, self.notes))
		base_coord.save(force_insert=force_insert)

	@classmethod
	def private(cls):
		return Coordinate.select().where(Coordinate.published == False)

	@classmethod
	def public(cls):
		return Coordinate.select().where(Coordinate.published == True)

	@classmethod
	def search(cls, query):
		words = [word.strip() for word in query.split() if word.strip()]
		if not words:
			# Return empty query
			return Coordinate.select().where(Coordinate.id == 0)
		else:
			search = ' '.join(words)

		return (FTSCoord
			.select(
				FTSCoord,
				Coordinate,
				FTSCoord.rank().alias('score'))
			.join(Coordinate, on=(FTSCoord.entry_id == Coordinate.id).alias('point'))
			.where(
				(Coordinate.published == True) &
				(FTSCoord.match(search)))
			.order_by(SQL('score').desc()))

# Full Text Search Model
class FTSCoord(FTSModel):
	entry_id = IntegerField(Coordinate)
	content = SearchField()

	class Meta:
		database = DATABASE

class Visit(Model):
	visit_date = DateField()
	coordinate = ForeignKeyField(
		rel_model=Coordinate,
		related_name='visits'
	)

	class Meta:
		database = DATABASE

class Weather(Model):
	


def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Team, User, Coordinate, FTSCoord], safe=True)
	DATABASE.close()