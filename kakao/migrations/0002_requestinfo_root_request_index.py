# Generated by Django 3.2.8 on 2021-11-19 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestinfo',
            name='root_request_index',
            field=models.IntegerField(default=-1),
        ),
    ]
