"""
Get historical weather data for new points.

Credit for dealing with sqlite3 parameter limitations goes to Francesco Montesano from stackoverflow question:
http://stackoverflow.com/questions/35616602/peewee-operationalerror-too-many-sql-variables-on-upsert-of-only-150-rows-8-c
"""
import datetime
from peewee import *
import time
import ulmo

import models


def get_coords():
	"""Get the coords that need weather data."""
	return models.Coordinate.get_coords_without_weather()


def get_weather_previous_years(coordinates):
	"""Fetches a time series of climate variables from the DAYMET single pixel
	extraction from 1980 to the latest full-calendar year.

	Uses NASA Daymet Single Pixel Extraction Tool:
		https://daymet.ornl.gov/dataaccess.html#SinglePixel
	"""
	for point in coordinates:
		# Store weather data as list of weather events
		weather_data = []
		# Temps are returned in centigrade
		data = ulmo.nasa.daymet.get_daymet_singlepixel(point.latitude, point.longitude, 
			variables=['tmax', 'tmin', 'prcp'], as_dataframe=True)

		# Convert to Fahrenheit
		data['tmax'] = data['tmax'].apply(lambda x: x * (9/5) + 32)
		data['tmin'] = data['tmin'].apply(lambda x: x * (9/5) + 32)

		for idx, row in data.iterrows():
			weather_event = {
				'coordinate': point,
				'day_summary': None,

				'ft_0_time': int(time.mktime(idx.timetuple())),
				'ft_0_precip_intensity_max': None,
				'ft_0_precip_accumulation': row['prcp'],
				'ft_0_temp_min': row['tmin'],
				'ft_0_temp_max': row['tmax'],

				'ft_1_time': None,
				'ft_1_precip_intensity_max': None,
				'ft_1_precip_accumulation': None,
				'ft_1_temp_min': None,
				'ft_1_temp_max': None,

				'ft_2_time': None,
				'ft_2_precip_intensity_max': None,
				'ft_2_precip_accumulation': None,
				'ft_2_temp_min': None,
				'ft_2_temp_max': None,

				'ft_3_time': None,
				'ft_3_precip_intensity_max': None,
				'ft_3_precip_accumulation': None,
				'ft_3_temp_min': None,
				'ft_3_temp_max': None,

				'ft_4_time': None,
				'ft_4_precip_intensity_max': None,
				'ft_4_precip_accumulation': None,
				'ft_4_temp_min': None,
				'ft_4_temp_max': None,

				'ft_5_time': None,
				'ft_5_precip_intensity_max': None,
				'ft_5_precip_accumulation': None,
				'ft_5_temp_min': None,
				'ft_5_temp_max': None,

				'ft_6_time': None,
				'ft_6_precip_intensity_max': None,
				'ft_6_precip_accumulation': None,
				'ft_6_temp_min': None,
				'ft_6_temp_max': None,

				'ft_7_time': None,
				'ft_7_precip_intensity_max': None,
				'ft_7_precip_accumulation': None,
				'ft_7_temp_min': None,
				'ft_7_temp_max': None,
			}
			weather_data.append(weather_event)

		# Save to database one point at a time so memory isn't overwhelmed
		save_to_database(weather_data)


def max_sql_variables():
	"""Get the maximum number of arguments allowed in a query by the current
	sqlite3 implementation. Based on `this question
	`_

	Returns
	-------
	int
		inferred SQLITE_MAX_VARIABLE_NUMBER
	"""
	import sqlite3
	db = sqlite3.connect(':memory:')
	cur = db.cursor()
	cur.execute('CREATE TABLE t (test)')
	low, high = 0, 100000
	while (high - 1) > low: 
		guess = (high + low) // 2
		query = 'INSERT INTO t VALUES ' + ','.join(['(?)' for _ in
													range(guess)])
		args = [str(i) for i in range(guess)]
		try:
			cur.execute(query, args)
		except sqlite3.OperationalError as e:
			if "too many terms in compound SELECT" in str(e):
				high = guess
			else:
				raise
		else:
			low = guess
	cur.close()
	db.close()
	return low


def save_to_database(data):
	error = 0
	with models.DATABASE.atomic():
		SQLITE_MAX_VARIABLE_NUMBER = max_sql_variables()

		try:
			size = (SQLITE_MAX_VARIABLE_NUMBER // len(data[0])) -1
			# remove one to avoid issue if peewee adds some variable
			for i in range(0, len(data), size):
				models.Weather.insert_many(data[i:i+size]).upsert().execute()
				#models.Weather.insert_many(data).execute()
		except IntegrityError as e:
			error += 1
			print(e.args)
	if error > 0:
		print('{} Weather Event(s) were not able to be added.'.format(error))


def main():
	coordinates = get_coords()
	get_weather_previous_years(coordinates)

if __name__ == '__main__':
	main()