import os

class Config:   
    # PostgreSQL config
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'postgres'
    # Use localhost when running locally, container name when in Docker
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = '5432'
    POSTGRES_DB = 'ecommerce'
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis config
    # Use localhost when running locally, container names when in Docker
    REDIS_MASTER_HOST = os.environ.get('REDIS_MASTER_HOST', 'localhost')
    REDIS_MASTER_PORT = 6379
    REDIS_REPLICA_1_HOST = os.environ.get('REDIS_REPLICA_1_HOST', 'localhost')
    REDIS_REPLICA_1_PORT = int(os.environ.get('REDIS_REPLICA_1_PORT', 6380))
    REDIS_REPLICA_2_HOST = os.environ.get('REDIS_REPLICA_2_HOST', 'localhost')
    REDIS_REPLICA_2_PORT = int(os.environ.get('REDIS_REPLICA_2_PORT', 6381))
    
    # Cache TTL in seconds (30 minutes)
    CACHE_TTL = 1800
    
    # Key prefixes
    CART_KEY_PREFIX = 'cart:'
    PRODUCT_STATS_KEY = 'stats:top_products'