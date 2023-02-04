import pickle
import random
import string
import os, base64
import sys
import json
from datetime import datetime, timedelta
from typing import Optional
from urllib import parse

# third party imports
# -------------------

from fastapi import APIRouter, status, Security
from fastapi import BackgroundTasks, Request, Form, Depends
#from fastapi_mail.fastmail import FastMail
from fastapi import Header, File, Body, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import (
    OAuth2,
    OAuthFlowsModel,
    get_authorization_scheme_param,
)

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from jwt import PyJWTError
from jose import JWTError, jwt


from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from pydantic import BaseModel, EmailStr, ValidationError

from passlib.context import CryptContext
import requests as rq
import msal


from app.services.models import Users
from sqlalchemy.orm import Session
from app.services.models import SessionLocal, engine
from app.services import crud
from app.services import schemas
from app.services import weather_service



security_router = APIRouter()

template_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
#template_dir = os.path.join(template_dir, "E")
# template_dir = os.path.join(template_dir, "website")
# template_dir = os.path.join(template_dir, "templates")
# print(template_dir)



SECRET_KEY = "bfdhvsdvfakuydgvfkajhsvlawegfUIFBVLjhvfulYFVsyuVFjavsfljv"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 3
COOKIE_AUTHORIZATION_NAME = "Authorization"
# COOKIE_DOMAIN = 'https://fast-wave-91117.herokuapp.com/'
# give the time for each token.
# Note: it is in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30
COOKIE_DOMAIN = "127.0.0.1"

PROTOCOL = "http://"
FULL_HOST_NAME = "localhost"
PORT_NUMBER = 8000



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="token",
#     scopes={"me": "Read information about the current user.", "items": "Read items."},
# )


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        auto_error: bool = False,
    ):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )
        print(" -----------------------------------")
        print(header_scheme)
        print(cookie_scheme)
        print(" -----------------------------------")

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param
            print("the authorization in the url is {}".format("header"))

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param
            print("the authorization in the url is {}".format("cookie"))

        else:
            authorization = False
            print("the authorization in the url is {}".format(False))

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param



oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")



@security_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
    ):
    """
        Takes in the OAuth2PasswordRequestForm and returns the access token.
    """
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # if isinstance(user.position, list) else [user.position]
    # print(user_scope)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)#30 min
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = JSONResponse({
        "status_code":status.HTTP_401_UNAUTHORIZED,
        "details": "invalid credentials",
        "message": "unauthorized",
    })
    try:
        
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub").encode('utf-8')
        # email = base64.b64decode(email)
        # username = aes_decrypt(username)
        if email is None:
            return None
    except JWTError:
        return None
    user = crud.get_user(db, email)
    if user is None:
        return None
    return user


def verify_password(plain_password, hashed_password):
    """This verifies that the hashed_password in DB is same as what user enters."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generates hash for the password."""
    return pwd_context.hash(password)





def authenticate_user(db, username: str, password: str):
    """
    First gets the user with get_user function, then
    verifies its password with the password entered at the front end.
    Parameters
    ----------
    username : str
        The username that the user entered.
        
    password : str
        The password entered by the user.
    Returns
    -------
    user : UserInDB
        The user info.
    """
    user = crud.get_user(db, username)
    print(user)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user



def create_user(db: Session, user: schemas.NewUser):
    user_presence = crud.get_user(db, user.email)
    # username_presence = crud.get_user(db, user.name).first()

    if user_presence: # or username_presence:
        return False
    secret_password = user.password
    db_user = Users(email=user.email, password=secret_password)
    db.add(db_user)
    db.flush()
    # user_role = db.query(Roles).filter(models.Roles.role_name == user.role).first()
    # assign_role = models.UserRoles(user_id=db_user.user_id, role_id=user_role.role_id, created_by=db_user.user_id,
                                #    updated_by=db_user.user_id)
    # db.add(assign_role)
    # db.flush()
    # user_auth = model(user_id=db_user.user_id, ip_address="192.168.0.1", session_id=make_session(), last_logged_in=datetime.now())
    # db.add(user_auth)
    # db.flush()
    db.commit()
    return True



@security_router.post("/signup")
async def new_user(
    user: schemas.NewUser,
    redirect_url: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        user.password = get_password_hash(user.password)
        signup_status = create_user(db, user)

        if signup_status is False:
            return JSONResponse({
                "status_code":status.HTTP_303_SEE_OTHER,
                "data":None,
                "message": "user exists"
                })
        else:
            return JSONResponse({
                "status_code": status.HTTP_201_CREATED,
                "data": None,
                "message": "signed up successfully"
                })
    except:
       return JSONResponse({
           "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
           "data": None,
           "message": "internal server error"
           })


# @security_router.get("/login")
# def login_user_page(request: schemas.NewUser, db: Session = Depends(get_db)):
#     """Redirects to the user login or sign in page"""
    
#     #auth_url = _build_auth_url(scopes=SCOPE,state="/"+redirect_url)
#     print("Redirect url",redirect_url)
#     return templates.TemplateResponse("login.html", {"request": request, "redirect":redirect_url})


@security_router.post("/authenticate", response_model=schemas.Token)
async def check_user_and_make_token(request: schemas.NewUser, db: Session = Depends(get_db)):
    # formdata = await request.form()
    # print(request)
    # print(formdata)
    #print("the scopes are .......")
    #print(formdata.scopes)
    # print(formdata["username"],formdata["password"])
    authenticated_user = authenticate_user(db, request.email,request.password)
    print(request.email)
    print(authenticated_user)
    if authenticated_user is None:
        return JSONResponse({'status_code':status.HTTP_401_UNAUTHORIZED,
            'detail':"Invalid username or password"})

    # if authenticated_user.active_yn==False:
    #     return JSONResponse({
    #         'status_code':status.HTTP_401_UNAUTHORIZED,
    #          'detail':"User Not Activated. Please verify email"
    #          })


    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)


    # user_scope = authenticated_user.position# if isinstance(authenticated_user.position, list) else [authenticated_user.position]
    # print("the user scope is........")
    # print(user_scope)
    access_token = create_access_token(
        data={"sub": authenticated_user.email}, expires_delta=access_token_expires
    )

    #################### SUCCESSFULLY LOGED IN USING CUSTOM DETAILS ######################
    #crud.logged_in(authenticated_user.id,"custom",request)

    token = jsonable_encoder(access_token)
    print("token is----------------------")
    print(token)
    response = JSONResponse({"access_token": token, "token_type": "bearer"})
    
    response.set_cookie(
        key=COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=10800,          # 3 hours
        expires=10800,          # 3 hours
    )
    print(response.__dict__)
    return response

def get_current_active_user(current_user: schemas.UserBase = Depends(get_current_user)):
    # , current_google_user: User = Depends(get_current_google_user)
    """
    """
    print("the current active user is.......")
    print(current_user)
    return current_user

@security_router.post("/weather_info")
async def weather_info(db: Session = Depends(get_db)):
    reports=weather_service.get_weather_report(0, 30)
    return reports





@security_router.get("/logout")
async def logout_and_remove_cookie( current_user: schemas.UserBase = Depends(get_current_active_user), db: Session = Depends(get_db)) -> "RedirectResponse":
    response = JSONResponse({
        'status_code':status.HTTP_401_UNAUTHORIZED,
        'url':'/login',
        'detail':'not logged in to logout.'})

    # if not current_user:
    
    if current_user is None:
        return response
    # usertype = crud.get_user_third_party(current_user.email)
    # if usertype=="google":
    #     return templates.TemplateResponse("google_signout.html", {"request": request})
    # else:
    response.delete_cookie(key=COOKIE_AUTHORIZATION_NAME, domain=COOKIE_DOMAIN)
    #crud.logged_out(current_user.email)
    # return templates.TemplateResponse("logout.html",{"request":request, "instanceid":"13917092-3f6f-49e5-b39b-e21c89f24565"})
    return response

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        '''
DateTime.UtcNow tells you the date and time as it would be in Coordinated Universal Time, 
which is also called the Greenwich Mean Time time zone. and used for to store the dates and time.
'''
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=3)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

