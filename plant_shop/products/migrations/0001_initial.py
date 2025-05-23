# Generated by Django 5.2 on 2025-05-07 06:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, upload_to='categories/')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('original_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('image', models.ImageField(upload_to='plants/')),
                ('care_level', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='easy', max_length=10)),
                ('light', models.CharField(choices=[('low', 'Low Light'), ('medium', 'Medium Light'), ('high', 'Bright Light')], default='medium', max_length=10)),
                ('pet_friendly', models.BooleanField(default=False)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('available', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plants', to='products.category')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
