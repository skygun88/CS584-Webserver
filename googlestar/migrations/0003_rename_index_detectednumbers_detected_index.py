# Generated by Django 3.2.8 on 2021-11-26 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('googlestar', '0002_remove_candidates_is_area_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detectednumbers',
            old_name='index',
            new_name='detected_index',
        ),
    ]
