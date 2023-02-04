from fastapi import FastAPI
import requests
import sqlalchemy as sqla
from app.api import api_router
from app.security import security_router
from fastapi_pagination import Page, paginate, add_pagination
from app.services.models import check_db_tables, get_db#engine, Users, Weather, Cities, SQLALCHEMY_DATABASE_URL
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.weather_service import insert_weather


app = FastAPI()
app.include_router(api_router)
app.include_router(security_router)
add_pagination(app)


# @api_router.on_event('startup')
# def init_data(db:Session = Depends(get_db)):
	



@app.on_event("startup")
def init_data():
    if check_db_tables():
        print("tables created")
        scheduler=BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(insert_weather,'cron',id='job1',second="*/10")

    else:
        print("database not available. please create it before starting the application")

    



@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/get_cities/{city_id}")
# async def read_item(city_id: int):
#     response=requests.get("https://api.openweathermap.org/data/2.5/weather?id={}&appid={}".format(819827,"ff0683e0250fb5cf09942d190af7abe1"))
#     print(response.json())
#     return {"message": "got the city"}