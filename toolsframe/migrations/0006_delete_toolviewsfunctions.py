# Generated by Django 4.1 on 2022-08-27 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toolsframe', '0005_alter_category_id_alter_suggestedtool_id_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ToolViewsFunctions',
        ),
    ]
