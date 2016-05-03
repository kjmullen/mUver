# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 22:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('muver_api', '0006_userprofile_stripe_account_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='billing_saved',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='customer_id',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
    ]
