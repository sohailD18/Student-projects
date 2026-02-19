"""
Context processors for Multi-Vendor Marketplace
"""

def vendor_cart(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            return {
                'cart': cart,
                'cart_total_items': cart.total_items,
                'cart_total_price': cart.total_price,
            }
        except:
            pass
    return {
        'cart': None,
        'cart_total_items': 0,
        'cart_total_price': 0,
    }
