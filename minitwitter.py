from app import app_factory, db 
# from the app module, import the app variable (an instance of the Flask class, as defined in app/__init__.py). Note: importing a module automatically exposes the content of its __init__.py file; this fact makes `from app import app` valid.
from app.models import User, Post

app = app_factory()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}