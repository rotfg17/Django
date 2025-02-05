# Generated by Django 5.1.1 on 2024-09-26 01:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='products',
        ),
        migrations.AddField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.date(2024, 9, 25)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cart',
            name='is_denied',
            field=models.BooleanField(default=False),
        ),
    ]
