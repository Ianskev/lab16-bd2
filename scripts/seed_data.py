from app import create_app
from app.models.database import db, DBCart, DBCartItem
from datetime import datetime, timezone
import random

def seed_database():
    app = create_app()
    
    # Product list with realistic items
    products = [
        {"name": "Laptop Dell XPS 13", "price": 1299.99},
        {"name": "Mouse Inalámbrico Logitech", "price": 29.99},
        {"name": "Monitor Samsung 27\"", "price": 299.99},
        {"name": "Teclado Mecánico Redragon", "price": 89.99},
        {"name": "Audífonos Bluetooth Sony", "price": 149.99},
        {"name": "Smartphone Samsung Galaxy S21", "price": 899.99},
        {"name": "Tablet Apple iPad Pro", "price": 799.99},
        {"name": "Smartwatch Apple Watch", "price": 399.99},
        {"name": "Cámara Digital Canon EOS", "price": 649.99},
        {"name": "Impresora HP LaserJet", "price": 249.99},
        {"name": "Disco Duro Externo 2TB", "price": 79.99},
        {"name": "Memoria USB 64GB", "price": 19.99},
        {"name": "Router WiFi TP-Link", "price": 59.99},
        {"name": "Auriculares Gaming HyperX", "price": 99.99},
        {"name": "Cable HDMI 2m", "price": 9.99},
        {"name": "Batería Portátil 10000mAh", "price": 39.99},
        {"name": "Funda para Laptop", "price": 24.99},
        {"name": "Base Refrigerante para Laptop", "price": 34.99},
        {"name": "Webcam Logitech HD", "price": 69.99},
        {"name": "Micrófono Blue Yeti", "price": 129.99},
        {"name": "Tarjeta Gráfica NVIDIA RTX 3060", "price": 399.99},
        {"name": "Procesador AMD Ryzen 7", "price": 329.99},
        {"name": "Memoria RAM 16GB DDR4", "price": 89.99},
        {"name": "Placa Base ASUS Prime", "price": 149.99},
        {"name": "SSD Samsung 1TB", "price": 119.99},
        {"name": "Fuente de Alimentación 650W", "price": 79.99},
        {"name": "Gabinete PC Gaming", "price": 69.99},
        {"name": "Silla Gaming", "price": 179.99},
        {"name": "Escritorio para Computadora", "price": 149.99},
        {"name": "Monitor Curvo Ultrawide", "price": 449.99},
    ]
    
    with app.app_context():
        # Clean existing data
        DBCartItem.query.delete()
        DBCart.query.delete()
        
        # Create 20 test carts
        for i in range(1, 21):
            user_id = f"user{i}"
            
            # Create cart
            cart = DBCart(
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.session.add(cart)
            db.session.flush()  # To get the cart ID
            
            # Add between 3 and 10 items to each cart
            num_items = random.randint(3, 10)
            
            # Select random products for the cart without repetition
            selected_products = random.sample(products, num_items)
            
            for product_idx, product in enumerate(selected_products):
                item = DBCartItem(
                    cart_id=cart.id,
                    product_id=product_idx + 1,
                    name=product["name"],
                    price=product["price"],
                    quantity=random.randint(1, 5),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.session.add(item)
        
        db.session.commit()
        print(f"✅ Test data inserted successfully: 20 carts with 3-10 items each")

if __name__ == '__main__':
    seed_database()