from django.db import models
from django.contrib.auth.models import User
from plant_shop.products.models import Plant

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('apple', 'Apple Pay'),
    ]
    
    SHIPPING_CHOICES = [
        ('standard', 'Standard Shipping'),
        ('express', 'Express Shipping'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='standard')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=5.99)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    # Stripe fields
    stripe_id = models.CharField(max_length=250, blank=True)
    
    # Razorpay fields
    razorpay_payment_id = models.CharField(max_length=250, blank=True)
    razorpay_order_id = models.CharField(max_length=250, blank=True)
    razorpay_signature = models.CharField(max_length=250, blank=True)
    
    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all()) + self.shipping_cost

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-updated']
        verbose_name_plural = 'Shipping addresses'
    
    def __str__(self):
        return f"{self.name}'s address"