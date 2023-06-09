# Generated by Django 4.1.7 on 2023-04-16 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('roles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_target', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='+', to='roles.roletarget')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Markdown text')),
                ('order', models.FloatField(default=0.0, help_text='Section order in its article.')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.article')),
                ('role_target', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='+', to='roles.roletarget')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='section',
            index=models.Index(fields=['article', 'order'], name='wiki_sectio_article_719adc_idx'),
        ),
    ]
