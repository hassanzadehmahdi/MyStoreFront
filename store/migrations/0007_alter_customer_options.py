# Generated by Django 5.2.3 on 2025-07-21 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_order_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name', 'user__last_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]
