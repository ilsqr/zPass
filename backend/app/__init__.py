from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///zpass.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token doesn't expire for simplicity
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.vault import vault_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vault_bp, url_prefix='/api/vault')
    
    # Add test endpoint
    @app.route('/')
    def index():
        return {'message': 'zPass Backend API is running!', 'version': '1.0.0'}
    
    @app.route('/api/test')
    def test():
        return {'message': 'API test successful', 'endpoints': [
            'POST /api/auth/register',
            'POST /api/auth/login', 
            'GET /api/auth/verify',
            'GET /api/vault',
            'PUT /api/vault'
        ]}
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
