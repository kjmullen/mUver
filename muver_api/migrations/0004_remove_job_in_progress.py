# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 21:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muver_api', '0003_job'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='in_progress',
        ),
    ]