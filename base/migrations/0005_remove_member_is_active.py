# Generated by Django 5.2 on 2025-05-03 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_transaction_amount_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='is_active',
        ),
    ]
