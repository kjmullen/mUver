# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('muver_api', '0009_auto_20160503_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='confirmation_mover',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='job',
            name='confirmation_user',
            field=models.BooleanField(default=False),
        ),
    ]
