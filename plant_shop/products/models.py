from django.db import models

# Create your models here.

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Plant(models.Model):
    CARE_LEVEL_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    LIGHT_CHOICES = [
        ('low', 'Low Light'),
        ('medium', 'Medium Light'),
        ('high', 'Bright Light'),
    ]
    
    category = models.ForeignKey(Category, related_name='plants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='plants/')
    care_level = models.CharField(max_length=10, choices=CARE_LEVEL_CHOICES, default='easy')
    light = models.CharField(max_length=10, choices=LIGHT_CHOICES, default='medium')
    pet_friendly = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:plant_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_on_sale(self):
        return self.original_price is not None and self.original_price > self.price