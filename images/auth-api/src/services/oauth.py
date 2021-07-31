import datetime
import uuid

import requests
from authlib.integrations.flask_client import OAuth
from authlib.jose import jwt
from authlib.oidc.core import CodeIDToken
from flask import url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

import models
from cache import redis_db
from db import db
from exceptions import (DeviceAlreadyExists, InvalidEmail, InvalidRefreshToken,
                        RoleAlreadyExists, UnknownDevice, UnknownRole,
                        UnknownUser)
from main import app

oauth = OAuth(app)
