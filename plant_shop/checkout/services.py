import stripe
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from .models import Order

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize Razorpay
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_payment_intent(order):
    """
    Create a Stripe PaymentIntent for the order
    """
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(order.get_total_cost() * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'customer_email': order.email
            }
        )
        return intent
    except Exception as e:
        print(f"Error creating payment intent: {str(e)}")
        return None

def create_razorpay_order(order):
    """
    Create a Razorpay order
    """
    try:
        # Create order data
        order_data = {
            'amount': int(order.get_total_cost() * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'order_{order.id}',
            'notes': {
                'order_id': str(order.id),
                'customer_email': order.email
            }
        }
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create(data=order_data)
        return razorpay_order
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

def verify_razorpay_payment(payment_id, order_id, signature):
    """
    Verify Razorpay payment signature
    """
    try:
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)
        return True
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return False

def process_payment(payment_intent_id, order):
    """
    Process the payment after successful payment intent confirmation
    """
    try:
        # Retrieve the payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Update order status
            order.paid = True
            order.stripe_id = payment_intent_id
            order.save()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            return True, "Payment successful"
        else:
            return False, "Payment failed"
            
    except Exception as e:
        return False, str(e)

def process_razorpay_payment(payment_id, order_id, signature, order):
    """
    Process Razorpay payment
    """
    try:
        # Verify payment
        if verify_razorpay_payment(payment_id, order_id, signature):
            # Update order status
            order.paid = True
            order.razorpay_payment_id = payment_id
            order.razorpay_order_id = order_id
            order.save()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            return True, "Payment successful"
        else:
            return False, "Payment verification failed"
    except Exception as e:
        return False, str(e)

def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    subject = f'Order Confirmation - Order #{order.id}'
    message = f'''
    Thank you for your order!
    
    Order Details:
    Order Number: {order.id}
    Total Amount: ${order.get_total_cost()}
    
    Shipping Address:
    {order.first_name} {order.last_name}
    {order.address}
    {order.city}, {order.state} {order.postal_code}
    
    We will process your order shortly.
    
    Best regards,
    Angel's Plant Shop Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    ) 