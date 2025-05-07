from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.PlantListView.as_view(), name='plant_list'),
    path('category/<slug:category_slug>/', views.PlantListView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.PlantDetailView.as_view(), name='plant_detail'),
]