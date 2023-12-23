# Generated by Django 4.1.7 on 2023-12-23 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0004_perfume_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfume',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfume',
            name='image',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='base_notes',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='fragrantica_url',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='middle_notes',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='olfactory_family',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='perfumesclub_uk_url',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='sephora_uk_url',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='perfume',
            name='top_notes',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
    ]
