# Generated by Django 3.0.7 on 2020-07-25 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend_api', '0029_auto_20200725_1223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='national_code',
        ),
    ]
