from app import create_app
from app.models.database import db, DBCart, DBCartItem
from datetime import datetime, timezone

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Limpiar datos existentes
        DBCartItem.query.delete()
        DBCart.query.delete()
        
        # Crear carritos de prueba
        test_carts = [
            {
                'user_id': 'user123',
                'items': [
                    {
                        'product_id': 1,
                        'name': 'Laptop Dell XPS 13',
                        'price': 1299.99,
                        'quantity': 1
                    },
                    {
                        'product_id': 2,
                        'name': 'Mouse Inalámbrico',
                        'price': 29.99,
                        'quantity': 2
                    }
                ]
            },
            {
                'user_id': 'user456',
                'items': [
                    {
                        'product_id': 3,
                        'name': 'Monitor 27"',
                        'price': 299.99,
                        'quantity': 1
                    },
                    {
                        'product_id': 4,
                        'name': 'Teclado Mecánico',
                        'price': 89.99,
                        'quantity': 1
                    },
                    {
                        'product_id': 5,
                        'name': 'Audífonos Bluetooth',
                        'price': 149.99,
                        'quantity': 1
                    }
                ]
            }
        ]
        
        # Insertar datos
        for cart_data in test_carts:
            cart = DBCart(
                user_id=cart_data['user_id'],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.session.add(cart)
            db.session.flush()  # Para obtener el ID del carrito
            
            for item_data in cart_data['items']:
                item = DBCartItem(
                    cart_id=cart.id,
                    product_id=item_data['product_id'],
                    name=item_data['name'],
                    price=item_data['price'],
                    quantity=item_data['quantity'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(item)
        
        db.session.commit()
        print("✅ Datos de prueba insertados correctamente")

if __name__ == '__main__':
    seed_database()