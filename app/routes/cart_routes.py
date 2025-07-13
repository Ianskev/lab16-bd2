from flask import Blueprint, jsonify, request
from app.services.cart_service import CartService

cart_bp = Blueprint('cart', __name__)
cart_service = CartService()

@cart_bp.route('/<user_id>', methods=['GET'])
def get_cart(user_id):
    cart = cart_service.get_cart(user_id)
    return jsonify(cart.to_dict())

@cart_bp.route('/<user_id>/add', methods=['POST'])
def add_to_cart(user_id):
    item_data = request.json
    cart = cart_service.add_item(user_id, item_data)
    return jsonify({'message': 'Item agregado', 'cart': cart.to_dict()})

@cart_bp.route('/<user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    cart = cart_service.remove_item(user_id, product_id)
    return jsonify({'message': 'Item eliminado', 'cart': cart.to_dict()})

@cart_bp.route('/<user_id>/update/<int:product_id>', methods=['PUT'])
def update_quantity(user_id, product_id):
    quantity = request.json.get('quantity')
    cart = cart_service.update_quantity(user_id, product_id, quantity)
    if cart:
        return jsonify({'message': 'Cantidad actualizada', 'cart': cart.to_dict()})
    return jsonify({'message': 'Producto no encontrado'}), 404

@cart_bp.route('/<user_id>/clear', methods=['POST'])
def clear_cart(user_id):
    cart_service.clear_cart(user_id)
    return jsonify({'message': 'Carrito limpiado'})