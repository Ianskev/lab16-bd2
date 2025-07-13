from flask import Blueprint, jsonify
from app.services.cart_service import CartService

stats_bp = Blueprint('stats', __name__)
cart_service = CartService()

@stats_bp.route('/top-products', methods=['GET'])
def get_top_products():
    """Return the top 10 most purchased products"""
    top_products = cart_service.get_top_products(10)
    return jsonify({
        'top_products': top_products
    }) 