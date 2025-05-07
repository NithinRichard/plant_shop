from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import stripe
from .forms import OrderCreateForm, AddressForm
from .models import Order, OrderItem, ShippingAddress
from plant_shop.cart.cart import Cart
from .services import (
    create_payment_intent,
    create_razorpay_order,
    process_payment,
    process_razorpay_payment
)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    plant=item['plant'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear the cart
            cart.clear()
            
            # Store order ID in session
            request.session['order_id'] = order.id
            
            # Create payment intent based on payment method
            payment_method = request.POST.get('payment_method')
            
            if payment_method == 'stripe':
                # Create Stripe payment intent
                intent = create_payment_intent(order)
                if intent:
                    return JsonResponse({
                        'clientSecret': intent.client_secret,
                        'order_id': order.id
                    })
                else:
                    return JsonResponse({
                        'error': 'Failed to create payment intent'
                    }, status=400)
            
            elif payment_method == 'razorpay':
                # Create Razorpay order
                razorpay_order = create_razorpay_order(order)
                if razorpay_order:
                    return JsonResponse({
                        'razorpay_order_id': razorpay_order['id'],
                        'amount': razorpay_order['amount'],
                        'currency': razorpay_order['currency'],
                        'order_id': order.id
                    })
                else:
                    return JsonResponse({
                        'error': 'Failed to create Razorpay order'
                    }, status=400)
            
            else:
                return JsonResponse({
                    'error': 'Invalid payment method'
                }, status=400)
    else:
        form = OrderCreateForm()
    
    return render(request, 'checkout/checkout.html', {
        'cart': cart,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
@require_POST
def payment_webhook(request):
    # Handle Stripe webhook
    if 'stripe-signature' in request.headers:
        try:
            event = stripe.Webhook.construct_event(
                request.body,
                request.headers['stripe-signature'],
                settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                order_id = payment_intent['metadata']['order_id']
                order = get_object_or_404(Order, id=order_id)
                
                success, message = process_payment(payment_intent['id'], order)
                if success:
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': message})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    # Handle Razorpay webhook
    elif 'x-razorpay-signature' in request.headers:
        try:
            # Verify webhook signature
            params_dict = {
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }
            
            razorpay_client.utility.verify_webhook_signature(
                request.body,
                request.headers['x-razorpay-signature'],
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            
            # Process payment
            order_id = request.POST.get('notes', {}).get('order_id')
            order = get_object_or_404(Order, id=order_id)
            
            success, message = process_razorpay_payment(
                params_dict['razorpay_payment_id'],
                params_dict['razorpay_order_id'],
                params_dict['razorpay_signature'],
                order
            )
            
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': message})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid webhook'})

def payment(request):
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('products:plant_list')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Here you would integrate with a payment gateway
    # For now, we'll just show a payment page
    
    return render(request, 'checkout/payment.html', {'order': order})

def payment_process(request):
    # This would handle the payment processing with a payment gateway
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('products:plant_list')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Simulate successful payment
    order.status = 'processing'
    order.save()
    
    # Redirect to order complete page
    return redirect('checkout:order_complete')

def payment_canceled(request):
    # Handle canceled payment
    messages.error(request, 'Payment was canceled.')
    return redirect('checkout:checkout')

def order_complete(request):
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('products:plant_list')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Clear order from session
    if 'order_id' in request.session:
        del request.session['order_id']
    
    return render(request, 'checkout/order_complete.html', {'order': order})

def order_confirmation(request, order_id):
    # Show order confirmation details
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/order_confirmation.html', {'order': order})

@login_required
def order_list(request):
    # Show list of user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'checkout/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    # Show details of a specific order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/order_detail.html', {'order': order})

@login_required
def address_list(request):
    # Show list of user's addresses
    addresses = ShippingAddress.objects.filter(user=request.user)
    return render(request, 'checkout/address_list.html', {'addresses': addresses})

@login_required
def address_add(request):
    # Add a new address
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is the first address or set as default
            if form.cleaned_data.get('is_default') or not ShippingAddress.objects.filter(user=request.user).exists():
                # Set all other addresses as not default
                ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True
            
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('checkout:address_list')
    else:
        form = AddressForm()
    
    return render(request, 'checkout/address_form.html', {'form': form})

@login_required
def address_edit(request, address_id):
    # Edit an existing address
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # If set as default
            if form.cleaned_data.get('is_default'):
                # Set all other addresses as not default
                ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True
            
            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('checkout:address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'checkout/address_form.html', {'form': form, 'address': address})

@login_required
def address_delete(request, address_id):
    # Delete an address
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        
        # If the deleted address was the default, set another as default if exists
        if address.is_default:
            first_address = ShippingAddress.objects.filter(user=request.user).first()
            if first_address:
                first_address.is_default = True
                first_address.save()
        
        return redirect('checkout:address_list')
    
    return render(request, 'checkout/address_confirm_delete.html', {'address': address})

@login_required
def address_set_default(request, address_id):
    # Set an address as default
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    # Set all addresses as not default
    ShippingAddress.objects.filter(user=request.user).update(is_default=False)
    
    # Set the selected address as default
    address.is_default = True
    address.save()
    
    messages.success(request, 'Default address updated.')
    return redirect('checkout:address_list')

def checkout_success(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'checkout/success.html', {'order': order})