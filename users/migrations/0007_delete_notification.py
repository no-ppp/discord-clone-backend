# Generated by Django 5.1.4 on 2025-01-20 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
