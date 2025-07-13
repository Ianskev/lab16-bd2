# Sistema de Carrito de Compras E-commerce

Este proyecto implementa un sistema transaccional de carrito de compras utilizando Flask, Redis para caché y PostgreSQL para almacenamiento persistente. El sistema utiliza el patrón Cache-Aside para optimizar el rendimiento y reducir la carga en la base de datos.

## Estructura del Proyecto

```
ecommerce/
├── app/
│   ├── __init__.py             # Inicialización de la aplicación Flask
│   ├── config.py               # Configuraciones de la aplicación
│   ├── cache/                  # Módulos de caché
│   │   ├── __init__.py
│   │   └── redis_client.py     # Implementación del cliente Redis
│   ├── models/                 # Modelos de datos
│   │   ├── database.py         # Modelos de base de datos
│   │   └── cart.py             # Modelos de negocio del carrito
│   ├── routes/                 # Rutas de la API
│   │   ├── cart_routes.py      # Endpoints del carrito
│   │   └── stats_routes.py     # Endpoints de estadísticas
│   └── services/               # Lógica de negocio
│       └── cart_service.py     # Servicio del carrito con patrón Cache-Aside
├── scripts/
│   ├── seed_data.py            # Script para poblar la base de datos
│   └── performance_test.py     # Script para pruebas de rendimiento
├── docker-compose.yml          # Configuración de replicación de Redis
├── requirements.txt            # Dependencias
└── run.py                      # Punto de entrada de la aplicación
```

## Configuración de Replicación de Redis

Este proyecto utiliza Redis en modo de replicación maestro-esclavo para alta disponibilidad y escalabilidad de lectura. La replicación consiste en:

1. **1 Nodo Maestro**: Maneja todas las operaciones de escritura
2. **2 Nodos Réplica**: Manejan operaciones de lectura para distribuir la carga

### Configuración de Docker Compose

La replicación de Redis está configurada usando Docker Compose:

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

### Puntos Clave de Configuración:

1. **Persistencia de Datos**: Todos los nodos utilizan la bandera `--appendonly yes` para habilitar la persistencia AOF, garantizando la durabilidad de los datos.
2. **Configuración de Replicación**: Los nodos réplica utilizan la opción `--replicaof` para especificar el nodo maestro.
3. **Configuración de Red**: Todos los nodos están en la misma red Docker para facilitar la comunicación.
4. **Mapeo de Puertos**: Cada instancia de Redis se expone en un puerto diferente para acceso externo:
   - Maestro: 6379
   - Réplica 1: 6380
   - Réplica 2: 6381

## Implementación del Patrón Cache-Aside

El patrón Cache-Aside está implementado en la clase `CartService`:

### Cómo Funciona:

1. **Operaciones de Lectura**:
   - Primero verifica si los datos existen en la caché Redis
   - Si se encuentra (acierto de caché), devuelve los datos
   - Si no se encuentra (fallo de caché), obtiene los datos de la base de datos
   - Almacena los datos obtenidos en caché para futuras solicitudes
   - Devuelve los datos

2. **Operaciones de Escritura**:
   - Actualiza primero la base de datos
   - Luego actualiza o invalida la caché

### Características Principales:

1. **Estructura de Claves de Caché**: Utiliza claves con prefijo (`cart:user_id`) para organizar datos
2. **TTL (Tiempo de Vida)**: Cada entrada en caché expira después de 30 minutos (1800 segundos)
3. **Carga de Lectura Distribuida**: Las operaciones de lectura utilizan nodos réplica de forma rotatoria
4. **Consolidación de Escritura**: Todas las operaciones de escritura van al nodo maestro

### Ejemplo de Código:

```python
def get_cart(self, user_id: str) -> Cart:
    """
    Implementación del patrón Cache-Aside:
    1. Intenta obtener del cache
    2. Si no está en cache, obtiene de la BD
    3. Actualiza el cache con los datos de la BD
    """
    # Intenta obtener el carrito de la caché primero
    cart_key = self._get_cart_key(user_id)
    cached_cart = redis_client.get_data(cart_key)
    
    if cached_cart:
        logger.info(f"Cache HIT para carrito: {user_id}")
        # Convierte los datos en caché a objeto Cart
        items = [
            CartItem(
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"]
            ) for item in cached_cart.get("items", [])
        ]
        return Cart(user_id=user_id, items=items)
    
    # Si no está en caché, obtiene de la base de datos
    logger.info(f"Cache MISS para carrito: {user_id}")
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
        
        # Actualiza la caché
        redis_client.set_data(cart_key, cart.to_dict(), self.cache_ttl)
        return cart
```

## Resultados de Rendimiento

La implementación del patrón Cache-Aside muestra mejoras significativas de rendimiento:

| Métrica | Respuesta en Caché | Respuesta sin Caché | Mejora |
|---------|-------------------|---------------------|--------|
| Tiempo de Respuesta Promedio | ~X ms | ~Y ms | ~Z% |
| Tiempo de Respuesta Mínimo | ~X ms | ~Y ms | - |
| Tiempo de Respuesta Máximo | ~X ms | ~Y ms | - |

*Nota: Los valores reales se completarán después de ejecutar las pruebas de rendimiento.*

## Endpoints

### Endpoints del Carrito:

- `GET /cart/<user_id>`: Obtener contenido del carrito
- `POST /cart/<user_id>/add`: Agregar ítem al carrito
- `POST /cart/<user_id>/remove/<product_id>`: Eliminar ítem del carrito
- `PUT /cart/<user_id>/update/<product_id>`: Actualizar cantidad de ítem
- `POST /cart/<user_id>/clear`: Limpiar carrito

### Endpoints de Estadísticas:

- `GET /stats/top-products`: Obtener los 10 productos más comprados

## Instrucciones de Configuración

1. **Clonar este repositorio**

2. **Configurar la replicación de Redis**:
   ```
   docker-compose up -d
   ```

3. **Crear la base de datos PostgreSQL**:
   ```sql
   CREATE DATABASE ecommerce;
   ```

4. **Instalar dependencias**:
   ```
   pip install -r requirements.txt
   ```

5. **Poblar la base de datos**:
   ```
   python -m scripts.seed_data
   ```

6. **Ejecutar la aplicación**:
   ```
   python run.py
   ```

7. **Probar rendimiento** (opcional):
   ```
   python -m scripts.performance_test
   ```

## Monitoreo de la Replicación de Redis

Para verificar el estado de la replicación:

```bash
# Conectar al maestro
docker exec -it redis-master redis-cli

# Verificar información de replicación
127.0.0.1:6379> info replication
```

Para verificar el estado de las réplicas:

```bash
# Conectar a la réplica
docker exec -it redis-replica-1 redis-cli

# Verificar información de replicación
127.0.0.1:6379> info replication
``` 5252