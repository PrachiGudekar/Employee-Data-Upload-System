from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    # Create a Flask application instance
    app = Flask(__name__)
    
    # Configure the application
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:********@localhost/mydatabase'
    app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key in production
    app.config['DEBUG'] = True  # Set to False in production
    
    # Initialize the SQLAlchemy object with the app
    db.init_app(app)

    # Use application context to avoid circular imports
    with app.app_context():
        # Import models and routes within the application context
        from models import Employee
        from routes import upload_file
        
        # Create all tables in the database (make sure to use this carefully in production)
        # db.create_all()
        
        # Register the blueprint for routes
        app.register_blueprint(upload_file)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Set debug to False in production
