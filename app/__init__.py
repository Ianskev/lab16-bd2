from flask import Flask
from app.routes.cart_routes import cart_bp
from app.routes.stats_routes import stats_bp
from app.models.database import db
from app.config import Config
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    
    # Check Redis connection
    from app.cache.redis_client import redis_client
    if redis_client.is_connected():
        app.logger.info("Successfully connected to Redis")
    else:
        app.logger.error("Failed to connect to Redis")
    
    return app