from flask import Blueprint

router = Blueprint('router', __name__)

from . import account, auth, error_handlers, role
