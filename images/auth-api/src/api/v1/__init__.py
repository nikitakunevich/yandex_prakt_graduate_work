from flask import Blueprint

router = Blueprint('router', __name__)

from . import auth
from . import account
from . import error_handlers
from . import role
