# Generated by Django 4.1.7 on 2024-01-09 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0008_brand_perfumes'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfume',
            name='le_nez',
            field=models.TextField(blank=True, null=True),
        ),
    ]