# Generated by Django 3.2.8 on 2021-11-26 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('googlestar', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidates',
            name='is_area_code',
        ),
    ]
