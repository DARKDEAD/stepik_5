from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.debug = True
app.config.from_object(Config)
# app.run(host="127.0.0.1", port=8000)
db = SQLAlchemy(app)
migrate = Migrate(app, db)




from app import routes, models