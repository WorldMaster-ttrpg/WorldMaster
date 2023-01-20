# Generated by Django 4.1.5 on 2023-01-20 05:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('worlds', '0002_alter_world_description_alter_world_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=64, validators=[django.core.validators.MinLengthValidator(3)])),
                ('name', models.CharField(max_length=64, validators=[django.core.validators.MinLengthValidator(3)])),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worlds.world')),
            ],
        ),
        migrations.AddConstraint(
            model_name='plane',
            constraint=models.UniqueConstraint(fields=('world', 'slug'), name='unique_world_slug'),
        ),
    ]
