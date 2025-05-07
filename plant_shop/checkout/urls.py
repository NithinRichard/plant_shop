from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # Main checkout page
    path('', views.checkout, name='checkout'),
    
    # Payment processing
    path('payment/', views.payment, name='payment'),
    path('payment/process/', views.payment_process, name='payment_process'),
    path('payment/canceled/', views.payment_canceled, name='payment_canceled'),
    
    # Order completion and confirmation
    path('complete/', views.order_complete, name='order_complete'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Order tracking
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Address management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:address_id>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:address_id>/set-default/', views.address_set_default, name='address_set_default'),
    
    path('success/', views.checkout_success, name='checkout_success'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
]