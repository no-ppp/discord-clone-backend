# Generated by Django 5.1.4 on 2025-01-11 10:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_bio_customuser_is_online_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='blocked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blocked_friendships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendship',
            name='notes',
            field=models.TextField(blank=True, help_text='Prywatne notatki o znajomym', null=True),
        ),
        migrations.AddField(
            model_name='friendship',
            name='status',
            field=models.CharField(choices=[('active', 'Aktywna'), ('blocked', 'Zablokowana'), ('unfriended', 'Zakończona')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='friendship',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name='friendship',
            index=models.Index(fields=['user', 'status'], name='users_frien_user_id_c37fe5_idx'),
        ),
        migrations.AddIndex(
            model_name='friendship',
            index=models.Index(fields=['friend', 'status'], name='users_frien_friend__779366_idx'),
        ),
    ]
