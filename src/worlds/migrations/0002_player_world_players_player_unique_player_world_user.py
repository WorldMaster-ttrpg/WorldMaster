# Generated by Django 4.2 on 2023-04-20 16:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('worlds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worlds.world')),
            ],
        ),
        migrations.AddField(
            model_name='world',
            name='players',
            field=models.ManyToManyField(related_name='worlds', related_query_name='world', through='worlds.Player', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='player',
            constraint=models.UniqueConstraint(fields=('world', 'user'), name='unique_player_world_user'),
        ),
    ]
