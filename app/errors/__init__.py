from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers 
# import the errors.handlers module so that its
#registered with the blueprint