# E-commerce Shopping Cart System

This project implements a transactional shopping cart system using Flask, Redis for caching, and PostgreSQL for persistent storage. The system uses the Cache-Aside pattern to optimize performance and reduce database load.

## Project Structure

```
ecommerce/
├── app/
│   ├── __init__.py             # Flask app initialization
│   ├── config.py               # Application configurations
│   ├── cache/                  # Cache modules
│   │   ├── __init__.py
│   │   └── redis_client.py     # Redis client implementation
│   ├── models/                 # Data models
│   │   ├── database.py         # Database models
│   │   └── cart.py             # Cart business models
│   ├── routes/                 # API routes
│   │   ├── cart_routes.py      # Cart endpoints
│   │   └── stats_routes.py     # Statistics endpoints
│   └── services/               # Business logic
│       └── cart_service.py     # Cart service with Cache-Aside pattern
├── scripts/
│   ├── seed_data.py            # Database seeding script
│   └── performance_test.py     # Performance testing script
├── docker-compose.yml          # Redis replication setup
├── requirements.txt            # Dependencies
└── run.py                      # Application entry point
```

## Redis Replication Configuration

This project uses Redis in master-slave replication mode for high availability and read scalability. The replication consists of:

1. **1 Master Node**: Handles all write operations
2. **2 Replica Nodes**: Handle read operations to distribute load

### Docker Compose Setup

The Redis replication is configured using Docker Compose:

```yaml
version: '3'

services:
  redis-master:
    image: redis:latest
    container_name: redis-master
    ports:
      - "6379:6379"
    volumes:
      - ./redis-data/master:/data
    command: redis-server --appendonly yes
    networks:
      - redis-network

  redis-replica-1:
    image: redis:latest
    container_name: redis-replica-1
    ports:
      - "6380:6379"
    volumes:
      - ./redis-data/replica1:/data
    command: redis-server --appendonly yes --replicaof redis-master 6379
    depends_on:
      - redis-master
    networks:
      - redis-network

  redis-replica-2:
    image: redis:latest
    container_name: redis-replica-2
    ports:
      - "6381:6379"
    volumes:
      - ./redis-data/replica2:/data
    command: redis-server --appendonly yes --replicaof redis-master 6379
    depends_on:
      - redis-master
    networks:
      - redis-network

networks:
  redis-network:
    driver: bridge
```

### Key Configuration Points:

1. **Data Persistence**: All nodes use the `--appendonly yes` flag to enable AOF persistence, ensuring data durability.
2. **Replication Setup**: Replica nodes use the `--replicaof` option to specify the master node.
3. **Network Configuration**: All nodes are on the same Docker network for easy communication.
4. **Port Mapping**: Each Redis instance is exposed on a different port for external access:
   - Master: 6379
   - Replica 1: 6380
   - Replica 2: 6381

## Cache-Aside Pattern Implementation

The Cache-Aside pattern is implemented in the `CartService` class:

### How it Works:

1. **Read Operations**:
   - First check if the data exists in Redis cache
   - If found (cache hit), return the data
   - If not found (cache miss), fetch from the database
   - Store the fetched data in cache for future requests
   - Return the data

2. **Write Operations**:
   - Update the database first
   - Then update or invalidate the cache

### Key Features:

1. **Cache Key Structure**: Uses prefixed keys (`cart:user_id`) for organizing data
2. **TTL (Time To Live)**: Each cache entry expires after 30 minutes (1800 seconds)
3. **Distributed Read Load**: Read operations use replica nodes in a round-robin fashion
4. **Write Consolidation**: All write operations go to the master node

### Code Example:

```python
def get_cart(self, user_id: str) -> Cart:
    """
    Implementación del patrón Cache-Aside:
    1. Intenta obtener del cache
    2. Si no está en cache, obtiene de la BD
    3. Actualiza el cache con los datos de la BD
    """
    # Try to get cart from cache first
    cart_key = self._get_cart_key(user_id)
    cached_cart = redis_client.get_data(cart_key)
    
    if cached_cart:
        logger.info(f"Cache HIT for cart: {user_id}")
        # Convert cached data to Cart object
        items = [
            CartItem(
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"]
            ) for item in cached_cart.get("items", [])
        ]
        return Cart(user_id=user_id, items=items)
    
    # If not in cache, get from database
    logger.info(f"Cache MISS for cart: {user_id}")
    db_cart = DBCart.query.filter_by(user_id=user_id).first()
    
    if db_cart:
        items = [
            CartItem(
                product_id=item.product_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity
            ) for item in db_cart.items
        ]
        cart = Cart(user_id=user_id, items=items)
        
        # Update cache
        redis_client.set_data(cart_key, cart.to_dict(), self.cache_ttl)
        return cart
```

## Performance Results

The implementation of the Cache-Aside pattern shows significant performance improvements:

| Metric | Cached Response | Uncached Response | Improvement |
|--------|----------------|-------------------|-------------|
| Average Response Time | ~X ms | ~Y ms | ~Z% |
| Min Response Time | ~X ms | ~Y ms | - |
| Max Response Time | ~X ms | ~Y ms | - |

*Note: Actual values will be filled in after running the performance tests.*

## Endpoints

### Cart Endpoints:

- `GET /cart/<user_id>`: Get cart contents
- `POST /cart/<user_id>/add`: Add item to cart
- `POST /cart/<user_id>/remove/<product_id>`: Remove item from cart
- `PUT /cart/<user_id>/update/<product_id>`: Update item quantity
- `POST /cart/<user_id>/clear`: Clear cart

### Statistics Endpoints:

- `GET /stats/top-products`: Get top 10 most purchased products

## Setup Instructions

1. **Clone this repository**

2. **Set up Redis replication**:
   ```
   docker-compose up -d
   ```

3. **Create PostgreSQL database**:
   ```sql
   CREATE DATABASE ecommerce;
   ```

4. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Seed the database**:
   ```
   python -m scripts.seed_data
   ```

6. **Run the application**:
   ```
   python run.py
   ```

7. **Test performance** (optional):
   ```
   python -m scripts.performance_test
   ```

## Monitoring Redis Replication

To check the replication status:

```bash
# Connect to master
docker exec -it redis-master redis-cli

# Check replication info
127.0.0.1:6379> info replication
```

To check replica status:

```bash
# Connect to replica
docker exec -it redis-replica-1 redis-cli

# Check replication info
127.0.0.1:6379> info replication
``` 