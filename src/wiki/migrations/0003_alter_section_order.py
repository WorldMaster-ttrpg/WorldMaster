# Generated by Django 4.1.7 on 2023-03-07 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0002_section_wiki_sectio_article_719adc_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='order',
            field=models.FloatField(default=0.0, help_text='Section order in its article.'),
        ),
    ]
