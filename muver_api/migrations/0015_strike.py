# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-11 21:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('muver_api', '0014_userprofile_in_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='Strike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strikes', to='muver_api.UserProfile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strikes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]