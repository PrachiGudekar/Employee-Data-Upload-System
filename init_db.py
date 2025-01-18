# init_db.py
from app import create_app, db

app = create_app()

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) 

with app.app_context():
    print("About to create tables...")
    db.create_all()
    print("Tables should be created.")
    print("Database tables created!")
