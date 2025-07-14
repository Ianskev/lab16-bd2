class Config:   
    # PostgreSQL config
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'postgres'
    POSTGRES_HOST = 'postgres-ecommerce'
    POSTGRES_PORT = '5432'
    POSTGRES_DB = 'ecommerce'
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis config
    REDIS_MASTER_HOST = 'redis-master'
    REDIS_MASTER_PORT = 6379
    REDIS_REPLICA_1_HOST = 'redis-replica-1'
    REDIS_REPLICA_1_PORT = 6379
    REDIS_REPLICA_2_HOST = 'redis-replica-2'
    REDIS_REPLICA_2_PORT = 6379
    
    # Cache TTL in seconds (30 minutes)
    CACHE_TTL = 1800
    
    # Key prefixes
    CART_KEY_PREFIX = 'cart:'
    PRODUCT_STATS_KEY = 'stats:top_products'