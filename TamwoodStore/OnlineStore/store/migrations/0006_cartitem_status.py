# Generated by Django 5.1.1 on 2024-09-26 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_rename_date_of_purchase_purchasehistory_purchase_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')], default='P', max_length=1),
        ),
    ]
