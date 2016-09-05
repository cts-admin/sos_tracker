import re
import unittest

from playhouse.test_utils import test_database
from peewee import *

import sos_tracker
from models import User, Team, Coordinate, FTSCoord

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Team, User, Coordinate, FTSCoord], safe=True)

LOGIN_USER_DATA = {
	'email': 'test_0@example.com',
	'password': 'password'
}

class TeamModelTestCase(unittest.TestCase):
	@staticmethod
	def create_team():
		Team.create_team(
			name='Team Tester',
			institution='University of Utah',
			code='Testing123'
		)


class UserModelTestCase(unittest.TestCase):
	@staticmethod
	def create_users(count=2):
		TeamModelTestCase.create_team()
		team = Team.select().get()
		for i in range(count):
			User.create_user(
				username='test_user{}'.format(i),
				email='test_{}@example.com'.format(i),
				password='password',
				team=team
			)

	def test_create_user(self):
		with test_database(TEST_DB, (Team, User,)):
			self.create_users()
			self.assertEqual(User.select().count(), 2)
			self.assertNotEqual(
				User.select().get().password,
				'password'
			)

	def test_create_duplicate_username(self):
		with test_database(TEST_DB, (Team, User,)):
			self.create_users()
			with self.assertRaises(ValueError):
				User.create_user(
					username='test_user1',
					email='test_unique@example.com',
					password='password',
					team='Team Tester'
				)

	def test_create_duplicate_email(self):
		with test_database(TEST_DB, (Team, User,)):
			self.create_users()
			with self.assertRaises(ValueError):
				User.create_user(
					username='test_unique',
					email='test_1@example.com',
					password='password',
					team='Team Tester'
				)


class CoordModelTestCase(unittest.TestCase):
	def test_coord_creation(self):
		with test_database(TEST_DB, (Team, User, Coordinate)):
			UserModelTestCase.create_users()
			user = User.select().get()
			Coordinate.create(
				user=user,
				latitude=37.301507,
				longitude=-113.961580,
				name='Test Coord',
				pin='RED MAP PIN',
				notes='This is a test. This is only a test.',
				published='True'
			)
			point = Coordinate.select().get()

			self.assertEqual(
				Coordinate.select().count(),
				1
			)
			self.assertEqual(point.user, user)


class ViewTestCase(unittest.TestCase):
	def setUp(self):
		sos_tracker.app.config['TESTING'] = True
		sos_tracker.app.config['WTF_CSRF_ENABLED'] = False
		self.app = sos_tracker.app.test_client()


class UserViewsTestCase(ViewTestCase):
	def test_good_login(self):
		with test_database(TEST_DB, (Team, User,)):
			UserModelTestCase.create_users(1)
			rv = self.app.post('/login', data=LOGIN_USER_DATA)
			self.assertEqual(rv.status_code, 302)
			self.assertEqual(rv.location, 'http://localhost/')

	def test_bad_login(self):
		with test_database(TEST_DB, (Team, User,)):
			rv = self.app.post('/login', data=LOGIN_USER_DATA)
			self.assertEqual(rv.status_code, 200)

	def test_logout(self):
		with test_database(TEST_DB, (Team, User,)):
			# Create and login the user
			UserModelTestCase.create_users(1)
			rv = self.app.post('/login', data=LOGIN_USER_DATA)
			self.assertEqual(rv.status_code, 302)
			rv = self.app.post('/logout')
			self.assertEqual(rv.status_code, 302)
			self.assertEqual(rv.location, 'http://localhost/login')

	def test_logged_out_menu(self):
		rv = self.app.get('/')
		self.assertIn("register", rv.get_data(as_text=True).lower())
		self.assertIn("log in", rv.get_data(as_text=True).lower())

	def test_logged_in_menu(self):
		with test_database(TEST_DB, (Team, User,)):
			UserModelTestCase.create_users(1)
			self.app.post('/login', data=LOGIN_USER_DATA)
			rv = self.app.get('/')
			self.assertIn("private coordinates", rv.get_data(as_text=True).lower())
			self.assertIn("manual entry", rv.get_data(as_text=True).lower())
			self.assertIn("files", rv.get_data(as_text=True).lower())
			self.assertIn("upload", rv.get_data(as_text=True).lower())
			self.assertIn("download", rv.get_data(as_text=True).lower())
			self.assertIn("log out", rv.get_data(as_text=True).lower())


class CoordinateViewsTestCase(ViewTestCase):
	def test_empty_db(self):
		with test_database(TEST_DB, (Coordinate,)):
			rv = self.app.get('/')
			self.assertIn("no points have been added yet.", rv.get_data(as_text=True).lower())

	def test_public_point_create(self):
		point_data = {
			'latitude': 39.012566,
			'longitude': -113.261538,
			'name': 'Public Test Coord',
			'pin': 'RED MAP PIN',
			'notes': 'This is a test. This is only a test.',
			'published': True
		}
		slug = slug = re.sub('[^\w]+', '-', point_data['name'].lower())
		with test_database(TEST_DB, (Team, User, Coordinate)):
			UserModelTestCase.create_users(1)
			self.app.post('/login', data=LOGIN_USER_DATA)

			point_data['user'] = User.select().get()
			rv = self.app.post('/create', data=point_data)
			self.assertEqual(rv.status_code, 302)
			self.assertEqual(rv.location, 'http://localhost/' + slug)
			self.assertEqual(Coordinate.select().count(), 1)
			rv = self.app.get('/')
			self.assertIn(point_data['name'], rv.get_data(as_text=True))
			rv = self.app.get('/private')
			self.assertNotIn(point_data['name'], rv.get_data(as_text=True))


if __name__ == '__main__':
	unittest.main()
