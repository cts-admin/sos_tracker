"""
Query database for coordinates and update weather data for each point.

To be run periodically as a cron job.
"""
import json
import os
import urllib

import models

API_KEY = os.environ.get('SOS_FORECAST_API_KEY')


def main():
	coordinates = models.Coordinate.select()

	for point in coordinates:
		url = 'https://api.forecast.io/forecast/' + API_KEY + '/' + \
			str(point.latitude) + ',' + str(point.longitude)
		response = urllib.request.urlopen(url)
		encoding = response.info().get_content_charset('utf-8')
		raw = response.read()
		data = json.loads(raw.decode(encoding))

		day_summary = data['daily']['summary']

		ft_0_time = data['daily']['data'][0]['time']
		ft_0_precip_int_max = data['daily']['data'][0]['precipIntensityMax']
		try:
			ft_0_precip_accum = data['daily']['data'][0]['precipAccumulation']
		except KeyError:
			ft_0_precip_accum = 0
		ft_0_temp_min = data['daily']['data'][0]['temperatureMin']
		ft_0_temp_max = data['daily']['data'][0]['temperatureMax']

		ft_1_time = data['daily']['data'][1]['time']
		ft_1_precip_int_max = data['daily']['data'][1]['precipIntensityMax']
		try:
			ft_1_precip_accum = data['daily']['data'][1]['precipAccumulation']
		except KeyError:
			ft_1_precip_accum = 0
		ft_1_temp_min = data['daily']['data'][1]['temperatureMin']
		ft_1_temp_max = data['daily']['data'][1]['temperatureMax']

		ft_2_time = data['daily']['data'][2]['time']
		ft_2_precip_int_max = data['daily']['data'][2]['precipIntensityMax']
		try:
			ft_2_precip_accum = data['daily']['data'][2]['precipAccumulation']
		except KeyError:
			ft_2_precip_accum = 0
		ft_2_temp_min = data['daily']['data'][2]['temperatureMin']
		ft_2_temp_max = data['daily']['data'][2]['temperatureMax']

		ft_3_time = data['daily']['data'][3]['time']
		ft_3_precip_int_max = data['daily']['data'][3]['precipIntensityMax']
		try:
			ft_3_precip_accum = data['daily']['data'][3]['precipAccumulation']
		except KeyError:
			ft_3_precip_accum = 0
		ft_3_temp_min = data['daily']['data'][3]['temperatureMin']
		ft_3_temp_max = data['daily']['data'][3]['temperatureMax']

		ft_4_time = data['daily']['data'][4]['time']
		ft_4_precip_int_max = data['daily']['data'][4]['precipIntensityMax']
		try:
			ft_4_precip_accum = data['daily']['data'][4]['precipAccumulation']
		except KeyError:
			ft_4_precip_accum = 0
		ft_4_temp_min = data['daily']['data'][4]['temperatureMin']
		ft_4_temp_max = data['daily']['data'][4]['temperatureMax']

		ft_5_time = data['daily']['data'][5]['time']
		ft_5_precip_int_max = data['daily']['data'][5]['precipIntensityMax']
		try:
			ft_5_precip_accum = data['daily']['data'][5]['precipAccumulation']
		except KeyError:
			ft_5_precip_accum = 0
		ft_5_temp_min = data['daily']['data'][5]['temperatureMin']
		ft_5_temp_max = data['daily']['data'][5]['temperatureMax']

		ft_6_time = data['daily']['data'][6]['time']
		ft_6_precip_int_max = data['daily']['data'][6]['precipIntensityMax']
		try:
			ft_6_precip_accum = data['daily']['data'][6]['precipAccumulation']
		except KeyError:
			ft_6_precip_accum = 0
		ft_6_temp_min = data['daily']['data'][6]['temperatureMin']
		ft_6_temp_max = data['daily']['data'][6]['temperatureMax']

		ft_7_time = data['daily']['data'][7]['time']
		ft_7_precip_int_max = data['daily']['data'][7]['precipIntensityMax']
		try:
			ft_7_precip_accum = data['daily']['data'][7]['precipAccumulation']
		except KeyError:
			ft_7_precip_accum = 0
		ft_7_temp_min = data['daily']['data'][7]['temperatureMin']
		ft_7_temp_max = data['daily']['data'][7]['temperatureMax']

		weather_event = models.Weather.create(
			coordinate = point,
			day_summary = day_summary,

			ft_0_time = ft_0_time,
			ft_0_precip_intensity_max = ft_0_precip_int_max,
			ft_0_precip_accumulation = ft_0_precip_accum,
			ft_0_temp_min = ft_0_temp_min,
			ft_0_temp_max = ft_0_temp_max,

			ft_1_time = ft_1_time,
			ft_1_precip_intensity_max = ft_1_precip_int_max,
			ft_1_precip_accumulation = ft_1_precip_accum,
			ft_1_temp_min = ft_1_temp_min,
			ft_1_temp_max = ft_1_temp_max,

			ft_2_time = ft_2_time,
			ft_2_precip_intensity_max = ft_2_precip_int_max,
			ft_2_precip_accumulation = ft_2_precip_accum,
			ft_2_temp_min = ft_2_temp_min,
			ft_2_temp_max = ft_2_temp_max,

			ft_3_time = ft_3_time,
			ft_3_precip_intensity_max = ft_3_precip_int_max,
			ft_3_precip_accumulation = ft_3_precip_accum,
			ft_3_temp_min = ft_3_temp_min,
			ft_3_temp_max = ft_3_temp_max,

			ft_4_time = ft_4_time,
			ft_4_precip_intensity_max = ft_4_precip_int_max,
			ft_4_precip_accumulation = ft_4_precip_accum,
			ft_4_temp_min = ft_4_temp_min,
			ft_4_temp_max = ft_4_temp_max,

			ft_5_time = ft_5_time,
			ft_5_precip_intensity_max = ft_5_precip_int_max,
			ft_5_precip_accumulation = ft_5_precip_accum,
			ft_5_temp_min = ft_5_temp_min,
			ft_5_temp_max = ft_5_temp_max,

			ft_6_time = ft_6_time,
			ft_6_precip_intensity_max = ft_6_precip_int_max,
			ft_6_precip_accumulation = ft_6_precip_accum,
			ft_6_temp_min = ft_6_temp_min,
			ft_6_temp_max = ft_6_temp_max,

			ft_7_time = ft_7_time,
			ft_7_precip_intensity_max = ft_7_precip_int_max,
			ft_7_precip_accumulation = ft_7_precip_accum,
			ft_7_temp_min = ft_7_temp_min,
			ft_7_temp_max = ft_7_temp_max,
		)

		print(weather_event)


if __name__ == '__main__':
	main()