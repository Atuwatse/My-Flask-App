from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from dotenv import load_dotenv
import os

from models import db

# Load environment variables
load_dotenv()

app = Flask(__name__)


# Initialize cache
cache = Cache(app)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)
migrate = Migrate(app, db)




