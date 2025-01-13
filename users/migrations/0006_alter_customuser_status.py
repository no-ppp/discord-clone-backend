# Generated by Django 5.1.4 on 2025-01-13 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='status',
            field=models.CharField(choices=[('online', 'Online'), ('offline', 'Offline'), ('busy', 'Busy'), ('away', 'Away')], default='offline', max_length=20),
        ),
    ]
