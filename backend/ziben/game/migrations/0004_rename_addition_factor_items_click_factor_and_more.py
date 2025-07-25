# Generated by Django 5.2.3 on 2025-07-04 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_alter_inventory_id_alter_shopitem_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='items',
            old_name='addition_factor',
            new_name='click_factor',
        ),
        migrations.RenameField(
            model_name='items',
            old_name='multiplication_factor',
            new_name='timed_factor',
        ),
        migrations.AlterField(
            model_name='items',
            name='cost',
            field=models.BigIntegerField(),
        ),
    ]
