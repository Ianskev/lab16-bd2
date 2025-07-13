from app.models.cart import Cart, CartItem
from app.models.database import db, DBCart, DBCartItem
from app.cache.redis_client import redis_client
from app.config import Config
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CartService:
    def __init__(self):
        self.cart_key_prefix = Config.CART_KEY_PREFIX
        self.product_stats_key = Config.PRODUCT_STATS_KEY
        self.cache_ttl = Config.CACHE_TTL

    def _get_cart_key(self, user_id: str) -> str:
        """Generate Redis key for cart data"""
        return f"{self.cart_key_prefix}{user_id}"

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
            
        # No cart found, return empty cart
        return Cart(user_id=user_id, items=[])
    
    def save_cart(self, cart: Cart) -> None:
        """Save cart to both database and cache"""
        # Save to database
        db_cart = DBCart.query.filter_by(user_id=cart.user_id).first()
        if not db_cart:
            db_cart = DBCart(user_id=cart.user_id)
            db.session.add(db_cart)
            db.session.flush()
        
        # Create dictionary of existing items for quick lookup
        existing_items = {item.product_id: item for item in db_cart.items}
        new_items = {item.product_id: item for item in cart.items}
        
        # Update or insert items
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
                
                # Update product statistics for new items
                self._update_product_stats(str(cart_item.product_id), cart_item.quantity)
        
        # Remove items that are no longer in the cart
        for product_id, db_item in existing_items.items():
            if product_id not in new_items:
                db.session.delete(db_item)
        
        db.session.commit()
        
        # Update cache
        cart_key = self._get_cart_key(cart.user_id)
        redis_client.set_data(cart_key, cart.to_dict(), self.cache_ttl)
    
    def _update_product_stats(self, product_id: str, quantity: int) -> None:
        """Update product statistics in Redis"""
        redis_client.increment_counter(self.product_stats_key, product_id, quantity)
    
    def add_item(self, user_id: str, item_data: dict) -> Cart:
        cart = self.get_cart(user_id)
        new_item = CartItem(**item_data)
        cart.add_item(new_item)
        self.save_cart(cart)
        
        # Update product stats when adding items
        self._update_product_stats(str(new_item.product_id), new_item.quantity)
        
        return cart
    
    def remove_item(self, user_id: str, product_id: int) -> Cart:
        cart = self.get_cart(user_id)
        # Find the item to get its quantity before removing
        for item in cart.items:
            if item.product_id == product_id:
                # Update product stats in the negative direction
                self._update_product_stats(str(product_id), -item.quantity)
                break
                
        cart.remove_item(product_id)
        self.save_cart(cart)
        return cart
    
    def update_quantity(self, user_id: str, product_id: int, quantity: int) -> Optional[Cart]:
        cart = self.get_cart(user_id)
        
        # Find current quantity to calculate the difference
        current_quantity = 0
        for item in cart.items:
            if item.product_id == product_id:
                current_quantity = item.quantity
                break
                
        if cart.update_quantity(product_id, quantity):
            self.save_cart(cart)
            
            # Update product stats with the difference in quantity
            quantity_difference = quantity - current_quantity
            if quantity_difference != 0:
                self._update_product_stats(str(product_id), quantity_difference)
                
            return cart
        return None
    
    def clear_cart(self, user_id: str) -> None:
        # Clear from database
        db_cart = DBCart.query.filter_by(user_id=user_id).first()
        if db_cart:
            db.session.delete(db_cart)
            db.session.commit()
            
        # Clear from cache
        cart_key = self._get_cart_key(user_id)
        redis_client.delete_data(cart_key)
        
    def get_top_products(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get top products by purchase frequency"""
        return redis_client.get_top_values(self.product_stats_key, count)