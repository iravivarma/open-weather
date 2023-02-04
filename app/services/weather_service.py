from sqlalchemy.orm import Session
from app.constants import api_key, city_ids, city_names
import requests
from app.services import models, crud, schemas
from fastapi import Depends
from fastapi_pagination import Page, paginate, add_pagination

def serialize_weather_report(reports):
	final_report=[]
	for report in reports['list']:
		print(report)
		final_report.append({'id': report['id'], 'name': report['name'], 'weather': report['main'], 'description':report['weather'][0]['description']})

	print(final_report)
	return {"weather_report": final_report}

def get_weather_report( db:Session):
	url = 'https://api.openweathermap.org/data/2.5/group?id='+city_ids+'&units;=metric&appid='+api_key
	# url = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+str(api_key) #+.format("London", api_key)
	print(url)
	data = requests.get(url).json()
	final_report = serialize_weather_report(data)
	# # insert_weather(final_report, db)
	return final_report

def insert_weather(db:Session = Depends(models.get_db)):
	url = 'https://api.openweathermap.org/data/2.5/group?id='+city_ids+'&units;=metric&appid='+api_key
	# url = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+str(api_key) #+.format("London", api_key)
	print(url)
	data = requests.get(url).json()
	final_report = serialize_weather_report(data)

	
	for report in final_report['weather_report']:
		weather = report['weather']
		temp=weather.get('temp', None)
		feels_like=weather.get('feels_like', None)
		temp_min = weather.get('temp_min', None)
		temp_max = weather.get('temp_max', None)
		pressure = weather.get('pressure', None)
		humidity = weather.get('humidity', None)
		sea_level = weather.get('sea_level', None)
		grnd_level = weather.get('grnd_level', None)
		description = report.get('description', None) 
		print(report['id'], report['name'], crud.city_weather_status(db, report['id']))
		if crud.city_weather_status(db, report['id']) == False:
			record = models.Weather(city_id=report['id'],
				# city_name=report['city_name'],
				temp=temp,
				feels_like=feels_like,
				temp_min = temp_min,
				temp_max = temp_max,
				pressure = pressure,
				humidity = humidity,
				sea_level = sea_level,
				grnd_level = grnd_level,
				description = description
			)

			db.add(record)
			db.commit()
			db.refresh(record)

		else:
			record = db.query(models.Weather).filter(models.Weather.city_id == report['id'])
			record = record.update({'temp': temp, 'feels_like':feels_like, 'temp_min':temp_min, 'temp_max':temp_max, 'pressure':pressure, 'humidity':humidity, 'sea_level':sea_level, 'grnd_level':grnd_level, 'description':description})
			db.commit()
			# db.refresh()
		


def insert_cities(db:Session):

	for key, values in city_names.items():
		print(type(key),type(values))
		record=models.Cities(cityid=key,city_name=values)
		db.add(record)
		db.commit()
		db.refresh(record)


	# return {'id': data['id'], 'name': data['name'], 'weather': data['main'], 'description':data['weather'][0]['description']}

def get_weather_report_from_db(db:Session):
	
	records = db.query(models.Cities).join(models.Weather, models.Cities.cityid == models.Weather.city_id)
	records = records.with_entities(models.Cities.city_name, models.Weather.description, models.Weather.feels_like, models.Weather.grnd_level, models.Weather.humidity, models.Weather.pressure, models.Weather.sea_level, models.Weather.temp, models.Weather.temp_min, models.Weather.temp_max).all()
	weather_records = []
	for record in records:
		temp_ = {}
		temp_['city_name'] = record[0]
		temp_['description'] = record[1]
		temp_['feels_like'] = record[2]
		temp_['grnd_level'] = record[3]
		temp_['humidity'] = record[4]
		temp_['pressure'] = record[5]
		temp_['sea_level'] = record[6]
		temp_['temp'] = record[7]
		temp_['temp_min'] = record[8]
		temp_['temp_max'] = record[9]
		weather_records.append(schemas.Weather(**temp_))
	# print(record)
	return weather_records



def paginate_from_db(db:Session):
	
	records = db.query(models.Cities).join(models.Weather, models.Cities.cityid == models.Weather.city_id)
	records = records.with_entities(models.Cities.city_name, models.Weather.description, models.Weather.feels_like, models.Weather.grnd_level, models.Weather.humidity, models.Weather.pressure, models.Weather.sea_level, models.Weather.temp, models.Weather.temp_min, models.Weather.temp_max).all()
	return records
