from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Plant
from plant_shop.cart.forms import CartAddProductForm

class PlantListView(ListView):
    model = Plant
    template_name = 'products/plant_list.html'
    context_object_name = 'plants'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Plant.objects.filter(available=True)
        
        # Filter by category if provided
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Filter by care level if provided
        care_level = self.request.GET.get('care_level')
        if care_level:
            queryset = queryset.filter(care_level=care_level)
        
        # Filter by light requirement if provided
        light = self.request.GET.get('light')
        if light:
            queryset = queryset.filter(light=light)
        
        # Filter by pet friendly if provided
        pet_friendly = self.request.GET.get('pet_friendly')
        if pet_friendly:
            queryset = queryset.filter(pet_friendly=True)
        
        # Sort products
        sort = self.request.GET.get('sort', 'name')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Add category to context if filtering by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['category'] = get_object_or_404(Category, slug=category_slug)
        
        return context

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'products/plant_detail.html'
    context_object_name = 'plant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_form'] = CartAddProductForm()
        
        # Get related plants (same category)
        plant = self.get_object()
        related_plants = Plant.objects.filter(
            category=plant.category
        ).exclude(id=plant.id)[:4]
        context['related_plants'] = related_plants
        
        return context