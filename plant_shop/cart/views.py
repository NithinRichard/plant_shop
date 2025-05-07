from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from plant_shop.products.models import Plant
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, plant_id):
    cart = Cart(request)
    plant = get_object_or_404(Plant, id=plant_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            plant=plant,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    
    return redirect('cart:cart_detail')

def cart_remove(request, plant_id):
    cart = Cart(request)
    plant = get_object_or_404(Plant, id=plant_id)
    cart.remove(plant)
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, plant_id):
    cart = Cart(request)
    plant = get_object_or_404(Plant, id=plant_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            plant=plant,
            quantity=cd['quantity'],
            override_quantity=True
        )
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )
    
    return render(request, 'cart/cart_detail.html', {'cart': cart})