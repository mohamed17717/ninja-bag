# Generated by Django 2.2 on 2021-09-10 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_webrequest_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webrequest',
            name='created',
        ),
    ]