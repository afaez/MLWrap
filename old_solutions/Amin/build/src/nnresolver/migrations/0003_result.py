# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 14:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nnresolver', '0002_auto_20171122_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('TR', 'Training Result'), ('PR', 'Prediction Result')], default='TR', max_length=2)),
                ('result_text', models.TextField(default='No result text has been set.')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnresolver.Nnentry')),
            ],
        ),
    ]
