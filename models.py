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
	password = CharField(max_length=700)
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
	"""Model for weather data."""

	#Summary of the day as a whole using averages
	day_summary = TextField()

	# Zero days in the future (present day)
	ft_0_time = IntegerField()
	ft_0_precip_intensity_max = FloatField()
	ft_0_precip_accumulation = FloatField()
	ft_0_temp_min = FloatField()
	ft_0_temp_max = FloatField()

	# One day in the future
	ft_1_time = IntegerField()
	ft_1_precip_intensity_max = FloatField()
	ft_1_precip_accumulation = FloatField()
	ft_1_temp_min = FloatField()
	ft_1_temp_max = FloatField()

	# Two days in the future
	ft_2_time = IntegerField()
	ft_2_precip_intensity_max = FloatField()
	ft_2_precip_accumulation = FloatField()
	ft_2_temp_min = FloatField()
	ft_2_temp_max = FloatField()

	# Three days in the future
	ft_3_time = IntegerField()
	ft_3_precip_intensity_max = FloatField()
	ft_3_precip_accumulation = FloatField()
	ft_3_temp_min = FloatField()
	ft_3_temp_max = FloatField()

	# Four days in the future
	ft_4_time = IntegerField()
	ft_4_precip_intensity_max = FloatField()
	ft_4_precip_accumulation = FloatField()
	ft_4_temp_min = FloatField()
	ft_4_temp_max = FloatField()

	# Five days in the future
	ft_5_time = IntegerField()
	ft_5_precip_intensity_max = FloatField()
	ft_5_precip_accumulation = FloatField()
	ft_5_temp_min = FloatField()
	ft_5_temp_max = FloatField()

	# Six days in the future
	ft_6_time = IntegerField()
	ft_6_precip_intensity_max = FloatField()
	ft_6_precip_accumulation = FloatField()
	ft_6_temp_min = FloatField()
	ft_6_temp_max = FloatField()

	# Seven days in the future
	ft_7_time = IntegerField()
	ft_7_precip_intensity_max = FloatField()
	ft_7_precip_accumulation = FloatField()
	ft_7_temp_min = FloatField()
	ft_7_temp_max = FloatField()

	coordinate = ForeignKeyField(
		rel_model=Coordinate,
		related_name='forecasts'
	)

	class Meta:
		database = DATABASE


def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Team, User, Coordinate, FTSCoord, Weather, Visit], safe=True)
	DATABASE.close()