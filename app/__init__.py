from flask import Flask
from app.routes.cart_routes import cart_bp
from app.routes.stats_routes import stats_bp
from app.models.database import db
from app.config import Config
import logging
import time

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
    
    # Check Redis connection with retry
    max_retries = 3
    retry_count = 0
    connected = False
    
    while retry_count < max_retries and not connected:
        try:
            from app.cache.redis_client import redis_client
            if redis_client.is_connected():
                app.logger.info("Successfully connected to Redis")
                connected = True
            else:
                app.logger.warning(f"Failed to connect to Redis (attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                time.sleep(1)  # Wait for 1 second before retrying
        except Exception as e:
            app.logger.warning(f"Redis connection error: {e} (attempt {retry_count + 1}/{max_retries})")
            retry_count += 1
            time.sleep(1)  # Wait for 1 second before retrying
    
    if not connected:
        app.logger.error("Could not connect to Redis after multiple attempts. Some features may be unavailable.")
    
    return app