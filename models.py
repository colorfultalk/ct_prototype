import psycopg2, os
from playhouse.postgres_ext import *
from urllib.parse import urlparse
from datetime import datetime
import json

# for heroku db connection
url = urlparse(os.environ["DATABASE_URL"])
db = PostgresqlDatabase(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

class BaseModel(Model):
    class Meta:
        database = db

class Session(BaseModel):
    id = PrimaryKeyField()
    user = CharField()
    data = BinaryJSONField()
    expiration = DateTimeField()

class Item:
    def __init__(self, image_url=None, description=None, location=None):
        self.image_url = image_url
        self.description = description
        self.location = location

    def register():
        # TODO: send json to API server for register
        pass

class Location:
    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
