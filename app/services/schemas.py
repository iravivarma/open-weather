from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, ValidationError, validator
from fastapi import Form


class UserBase(BaseModel):
    name :str
    email: str
    
class NewUser(BaseModel):
    email: str
    password: str

class Weather(BaseModel):
    """
    Schema for final response validation
    """
    city_name: str = None
    description : str = None
    feels_like : str = None
    grnd_level:int = None
    humidity: int = None
    pressure : int = None
    sea_level:int = None
    temp :str = None
    temp_min : str = None
    temp_max : str = None
    

class login_user_schema(BaseModel):
    """
    Pydantic schema for user login
    Currently the username is same as email
    """
    # username: str
    # name: Optional[str] = None
    email: str = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    """
    JWT token schema
    """    
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes : str = None#List[str] = []

class authenticate_schema(BaseModel):
    email : str
    password : str
