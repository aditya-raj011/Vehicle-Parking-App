from flask import Flask
from application.database import db

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    # app.secret_key = "secret"
    db.init_app(app)
    app.app_context().push() 
    return app
app = create_app()

from application.controllers import*


if __name__ == "__main__":
    app.run()





