# Generated by Django 4.1.7 on 2023-12-23 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0002_perfume_accords'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=3000, null=True)),
                ('logo', models.CharField(blank=True, max_length=3000, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('fragrantica_url', models.CharField(blank=True, max_length=3000, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]