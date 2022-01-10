from fastapi import FastAPI
from cassandra.cqlengine.management import sync_table

from helpers import db
from models.auth import User
from routers.auth_router import auth_router
from routers.file_router import file_router


app = FastAPI()
session = None

@app.on_event("startup")
def on_startup():
    global session
    session = db.get_session()
    sync_table(User)
    
    
app.include_router(auth_router)
app.include_router(file_router)