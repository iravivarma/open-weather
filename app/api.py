from fastapi import APIRouter, Depends,HTTPException
import requests
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.services import crud
from app.services import models
from app.services import schemas
import uvicorn
from app.constants import city_ids, api_key
from fastapi.responses import JSONResponse
from app.services.weather_service import insert_weather
from app.services.models import SessionLocal, engine
from app.services import weather_service
from apscheduler.schedulers.background import BackgroundScheduler


from fastapi_pagination import Page, paginate, add_pagination


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app = Flask(__name__)
api_router = APIRouter(
	prefix="/api",
    tags=["Apis"],
)
@api_router.get('/weather/{city}')
def index(city: str):
	api_key = "68dc5e4867b789c2375072306a7e6631"
	url = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+str(api_key) #+.format("London", api_key)
	print(url)
	data = requests.get(url).json()
	# print(data.json())
	return {'id': data['id'], 'name': data['name'], 'weather': data['main'], 'description':data['weather'][0]['description']}


@api_router.get("/weather-api")
def weather_api(db:Session =Depends(get_db)):
	# api_key = "68dc5e4867b789c2375072306a7e6631"
	# url = 'https://api.openweathermap.org/data/2.5/group?id='+city_ids+'&units;=metric&appid='+api_key
	# # url = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+str(api_key) #+.format("London", api_key)
	# print(url)
	# data = requests.get(url).json()
	# print(data.json())
	# return {'id': data['id'], 'name': data['name'], 'weather': data['main'], 'description':data['weather'][0]['description']}
	return crud.insert_weather(db)#get_weather_report()


###Check if user Exists####
# @api_router.get("/users/{user_name}", response_model=app.services.schemas.Users)
# async def read_user(user_name: str, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_name=user_name).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
@api_router.post("/cities")
async def insertCities(db:Session =Depends(get_db)):
	return weather_service.insert_cities(db)


@api_router.get("/weather_report_all", response_model=Page[schemas.Weather])
async def pagination(db:Session =Depends(get_db)):
	reports = weather_service.get_weather_report_from_db(db)
	# json_compatible_item_data = jsonable_encoder(reports)
	return paginate(reports)


@api_router.post("/insert_weather")
async def insert_weather_info(db: Session = Depends(get_db)):
    reports=weather_service.insert_weather(db)
    return reports

@api_router.get("/db_weather_report")
async def weather_report_from_db(db: Session = Depends(get_db)):
	return  {"status": 200, "data":weather_service.get_weather_report_from_db(db), "message": "data received"}



if __name__ == '__main__':
	app.run(debug=True)