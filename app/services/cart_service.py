from app.models.cart import Cart, CartItem
from app.models.database import db, DBCart, DBCartItem
from typing import Optional

class CartService:
    def get_cart(self, user_id: str) -> Cart:
        # Buscar directamente en la base de datos
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
            return Cart(user_id=user_id, items=items)
            
        return Cart(user_id=user_id, items=[])
    
    def save_cart(self, cart: Cart) -> None:
        db_cart = DBCart.query.filter_by(user_id=cart.user_id).first()
        if not db_cart:
            db_cart = DBCart(user_id=cart.user_id)
            db.session.add(db_cart)
            db.session.flush()
        
        # Crear diccionario de items existentes para búsqueda rápida
        existing_items = {item.product_id: item for item in db_cart.items}
        new_items = {item.product_id: item for item in cart.items}
        
        # Actualizar o insertar items
        for product_id, cart_item in new_items.items():
            if product_id in existing_items:
                db_item = existing_items[product_id]
                db_item.name = cart_item.name
                db_item.price = cart_item.price
                db_item.quantity = cart_item.quantity
            else:
                db_item = DBCartItem(
                    cart_id=db_cart.id,
                    product_id=cart_item.product_id,
                    name=cart_item.name,
                    price=cart_item.price,
                    quantity=cart_item.quantity
                )
                db.session.add(db_item)
        
        # Eliminar items que ya no están en el carrito
        for product_id, db_item in existing_items.items():
            if product_id not in new_items:
                db.session.delete(db_item)
        
        db.session.commit()
    
    def add_item(self, user_id: str, item_data: dict) -> Cart:
        cart = self.get_cart(user_id)
        new_item = CartItem(**item_data)
        cart.add_item(new_item)
        self.save_cart(cart)
        return cart
    
    def remove_item(self, user_id: str, product_id: int) -> Cart:
        cart = self.get_cart(user_id)
        cart.remove_item(product_id)
        self.save_cart(cart)
        return cart
    
    def update_quantity(self, user_id: str, product_id: int, quantity: int) -> Optional[Cart]:
        cart = self.get_cart(user_id)
        if cart.update_quantity(product_id, quantity):
            self.save_cart(cart)
            return cart
        return None
    
    def clear_cart(self, user_id: str) -> None:
        db_cart = DBCart.query.filter_by(user_id=user_id).first()
        if db_cart:
            db.session.delete(db_cart)
            db.session.commit()