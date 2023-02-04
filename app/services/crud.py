from sqlalchemy.orm import Session
from app.services import schemas, models
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import load_only
from app.services.models import Users, Weather, Cities



def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Users).offset(skip).limit(limit).all()	

def get_user_email(db: Session, email: str):
	'''
	email: Input
	this gives output by Querying
	From : models-->Users(table)
	filters: email in models-->Users
	if model.email == input parameter
	it will return the User details as objects
	'''
	return db.query(models.Users).filter(models.Users.email == email).first()   

def get_user(db: Session, email: str):
	'''
	input: name of the User
	return the query from Users class in models.py and filter the
	user_name of the Users class by comparing with the input paramter.
	'''
	return db.query(Users).filter(Users.email == email).first()



def city_weather_status(db: Session, city_id: str):
	"""
	check weather of a given city id is present or not
	will be useful for updation of weather data instead of reinserting
	"""
	record = db.query(models.Weather).filter(models.Weather.city_id == city_id)
	if record.first() == None:
		return False
	else:
		return True


