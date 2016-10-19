"""
Get historical weather data for new points.
"""
import datetime
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
		# Temps are returned in centigrade
		data = ulmo.nasa.daymet.get_daymet_singlepixel(point.latitude, point.longitude, 
			variables=['tmax', 'tmin', 'prcp'], as_dataframe=True)

		# Convert to Fahrenheit
		data['tmax'] = data['tmax'].apply(lambda x: x * (9/5) + 32)
		data['tmin'] = data['tmin'].apply(lambda x: x * (9/5) + 32)

		#print("Point:", point)

		for idx, row in data.iterrows():
			#print("Row {}: {}".format(idx, row))
			weather_event = models.Weather.create(
				coordinate = point,
				day_summary = None,

				ft_0_time = int(time.mktime(idx.timetuple())),
				ft_0_precip_intensity_max = None,
				ft_0_precip_accumulation = row['prcp'],
				ft_0_temp_min = row['tmin'],
				ft_0_temp_max = row['tmax'],

				ft_1_time = None,
				ft_1_precip_intensity_max = None,
				ft_1_precip_accumulation = None,
				ft_1_temp_min = None,
				ft_1_temp_max = None,

				ft_2_time = None,
				ft_2_precip_intensity_max = None,
				ft_2_precip_accumulation = None,
				ft_2_temp_min = None,
				ft_2_temp_max = None,

				ft_3_time = None,
				ft_3_precip_intensity_max = None,
				ft_3_precip_accumulation = None,
				ft_3_temp_min = None,
				ft_3_temp_max = None,

				ft_4_time = None,
				ft_4_precip_intensity_max = None,
				ft_4_precip_accumulation = None,
				ft_4_temp_min = None,
				ft_4_temp_max = None,

				ft_5_time = None,
				ft_5_precip_intensity_max = None,
				ft_5_precip_accumulation = None,
				ft_5_temp_min = None,
				ft_5_temp_max = None,

				ft_6_time = None,
				ft_6_precip_intensity_max = None,
				ft_6_precip_accumulation = None,
				ft_6_temp_min = None,
				ft_6_temp_max = None,

				ft_7_time = None,
				ft_7_precip_intensity_max = None,
				ft_7_precip_accumulation = None,
				ft_7_temp_min = None,
				ft_7_temp_max = None,
			)


def main():
	coordinates = get_coords()
	get_weather_previous_years(coordinates)

if __name__ == '__main__':
	main()