# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-13 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('muver_api', '0025_auto_20160513_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='time_accepted',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
