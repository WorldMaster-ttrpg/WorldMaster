# Generated by Django 4.2.6 on 2023-11-04 21:36

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import worldmaster.maps.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('worlds', '0003_alter_entity_article_alter_entity_role_target_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Presence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.FloatField(blank=True, default=None, null=True, verbose_name='The time that this presence appeared')),
                ('end_time', models.FloatField(blank=True, default=None, null=True, verbose_name='The time that this presence disappeared')),
                ('shape', worldmaster.maps.fields.PolyhedralSurfaceField(dim=3, srid=4326)),
                ('position', django.contrib.gis.db.models.fields.PointField(dim=3, srid=4326, verbose_name='The position, or the starting position if end_position is set')),
                ('end_position', django.contrib.gis.db.models.fields.PointField(blank=True, default=None, dim=3, null=True, srid=4326, verbose_name='The end position, if the presence moved')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worlds.entity')),
                ('plane', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worlds.plane')),
            ],
        ),
        migrations.AddConstraint(
            model_name='presence',
            constraint=models.CheckConstraint(check=models.Q(('start_time__isnull', True), ('end_time__isnull', True), ('end_time__gt', models.F('start_time')), _connector='OR'), name='end_time_after_start_time', violation_error_message='If start_time and end_time exist, end_time must be greater than start_time'),
        ),
        migrations.AddConstraint(
            model_name='presence',
            constraint=models.CheckConstraint(check=models.Q(('end_position__isnull', True), models.Q(('start_time__isnull', False), ('end_time__isnull', False)), _connector='OR'), name='end_position_needs_time_span', violation_error_message='If end_position is not null, then start_time and end_time must not be null'),
        ),
        migrations.AddConstraint(
            model_name='presence',
            constraint=models.CheckConstraint(check=models.Q(('end_position', models.F('position')), _negated=True), name='end_position_different_from_start', violation_error_message='end_position must not equal position'),
        ),
    ]