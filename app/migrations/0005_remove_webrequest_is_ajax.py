# Generated by Django 4.1 on 2022-08-27 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_webrequest_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webrequest',
            name='is_ajax',
        ),
    ]
