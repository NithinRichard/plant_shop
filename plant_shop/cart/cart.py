from decimal import Decimal
from django.conf import settings
from plant_shop.products.models import Plant

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, plant, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        plant_id = str(plant.id)
        if plant_id not in self.cart:
            self.cart[plant_id] = {'quantity': 0, 'price': str(plant.price)}
        
        if override_quantity:
            self.cart[plant_id]['quantity'] = quantity
        else:
            self.cart[plant_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        # Mark the session as "modified" to make sure it gets saved
        self.session.modified = True
    
    def remove(self, plant):
        """
        Remove a product from the cart.
        """
        plant_id = str(plant.id)
        if plant_id in self.cart:
            del self.cart[plant_id]
            self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        plant_ids = self.cart.keys()
        # Get the product objects and add them to the cart
        plants = Plant.objects.filter(id__in=plant_ids)
        
        cart = self.cart.copy()
        for plant in plants:
            cart[str(plant.id)]['plant'] = plant
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calculate the total cost of items in the cart.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def get_shipping_cost(self):
        """
        Calculate the shipping cost based on the total price.
        """
        total_price = self.get_total_price()
        if total_price >= 100:  # Free shipping for orders over $100
            return Decimal('0.00')
        elif total_price >= 50:  # $5 shipping for orders between $50 and $100
            return Decimal('5.00')
        else:  # $10 shipping for orders under $50
            return Decimal('10.00')
    
    def get_total_price_with_shipping(self):
        """
        Calculate the total cost including shipping.
        """
        return self.get_total_price() + self.get_shipping_cost()
    
    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()